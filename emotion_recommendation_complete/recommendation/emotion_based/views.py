# emotion_recommendation/emotion_based/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import openai, os
from dotenv import load_dotenv
import re
from django.contrib.auth.models import User
#from recommendation.utils import log_recommendation, generate_recommendations
from rest_framework.permissions import AllowAny
from ..utils import log_recommendation, generate_recommendations

from django.views.decorators.csrf import csrf_exempt



dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv("OPENAI_API_KEY")




import os
# openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_movies_and_music(request):
    mood = request.data.get("most_frequent_mood")
    user = request.user if request.user.is_authenticated else None
    lines = generate_recommendations(mood, user=user)
    # 로그인된 사용자만 로그 기록 (로그인 안 됐으면 생략)
    if user:
        log_recommendation(user.id, mood, lines)
    return Response({"recommendations": "\n".join(lines)})


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
            cleaned_line = re.sub(r'^\d+\.\s*', '', line)
            if current_block == "movie":
                movie_lines.append(cleaned_line)
            elif current_block == "music":
                music_lines.append(cleaned_line)

    return movie_lines, music_lines

@api_view(['GET'])
@permission_classes([AllowAny])
def recommendation_result_view(request, user_id):
    print(f"recommendation_result_view called with user_id={user_id}")
    from django.contrib.auth.models import User
    from recommendation.utils import generate_recommendations
    
    user_obj = User.objects.get(id=user_id)
    recommendations = generate_recommendations(mood="기쁨", user=user_obj)
    
    context = {
        'recommendations': recommendations,
    }
    return Response({"recommendations": recommendations})