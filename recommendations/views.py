from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import openai, os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
import re
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from recommendations.models import Feedback
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_movies_and_music(request):
    """감정에 따라 적절한 영화와 음악을 추천하는 함수"""
    most_frequent_mood = request.data.get("most_frequent_mood")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"'{most_frequent_mood}' 감정을 가진 사람에게 추천할 "
                        f"대한민국 또는 외국 영화 3편과 음악 3곡을 각각 구분된 문단(예: '### 영화 추천' / '### 음악 추천') 아래에 항목별로 나열해줘. "
                        f"항목은 **숫자 없이** '제목 - 태그1, 태그2' 형식으로 한 줄씩 작성해줘. 중복 없이 제공해줘. "
                        f"예시:\n### 영화 추천\n기생충 - 드라마, 사회\n인셉션 - 스릴러, SF\n\n### 음악 추천\nDynamite - 팝, 댄스"
                                ),
                },
            ],
            max_tokens=600
        )

        raw_text = response.choices[0].message.content

        # ✅ 사용자의 dislike 항목 가져오기
        from commons.models import Feedback
        disliked_titles = set(
            Feedback.objects.filter(user=request.user, feedback="dislike")
            .values_list("item_title", flat=True)
        )

        # ✅ 추천 라인 필터링
        lines = raw_text.strip().splitlines()
        filtered_lines = [
            line for line in lines
            if not any(disliked_title.strip() in line for disliked_title in disliked_titles)
        ]

        cleaned_text = "\n".join(filtered_lines)

        return Response({"recommendations": cleaned_text})

    except openai.error.RateLimitError:
        return Response({"error": "현재 추천 기능이 제한되어 있습니다. 나중에 다시 시도해주세요."}, status=429)

def split_recommendations(recommendations_text):
    movie_lines = []
    music_lines = []

    current_block = None
    for line in recommendations_text.splitlines():
        line = line.strip()
        if "영화 추천" in line:
            current_block = "movie"
        elif "음악 추천" in line:
            current_block = "music"
        elif line and not line.startswith("###"):
            # 앞의 숫자 + 점 + 공백 제거 (예: "1. " 제거)
            cleaned_line = re.sub(r'^\d+\.\s*', '', line)
            if current_block == "movie":
                movie_lines.append(cleaned_line)
            elif current_block == "music":
                music_lines.append(cleaned_line)

    return movie_lines, music_lines


@require_POST
@login_required
def save_feedback(request):
    item_title = request.POST.get("item_title")
    item_type = request.POST.get("item_type")
    feedback = request.POST.get("feedback")

    Feedback.objects.update_or_create(
        user=request.user,
        item_title=item_title,
        item_type=item_type,
        defaults={"feedback": feedback}
    )
    return JsonResponse({"message": f"{'좋아요' if feedback == 'like' else '별로예요'}로 저장되었습니다."})
