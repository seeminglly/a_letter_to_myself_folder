# emotion/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from letters.models import Letters  # 편지 모델이 다른 앱에 있을 경우
from .utils import analyze_emotion_for_letter
from collections import Counter

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reanalyze_all_emotions(request):
    """해당 사용자의 모든 편지에 대해 감정 재분석"""
    user = request.user
    letters = Letters.objects.filter(user=user)

    for letter in letters:
        analyze_emotion_for_letter(letter)

    return Response({"status": "success"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_emotion_summary(request):
    """해당 사용자의 감정 통계 및 추천 결과"""
    user = request.user
    letters = Letters.objects.filter(user=user)

    emotion_list = [letter.mood for letter in letters if letter.mood]
    detailed_list = [letter.detailed_mood for letter in letters if letter.detailed_mood]

    emotion_counts = dict(Counter(emotion_list))
    detailed_counts = dict(Counter(detailed_list))

    most_frequent_mood = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
    most_frequent_detailed_mood = max(detailed_counts.items(), key=lambda x: x[1])[0] if detailed_counts else None

    return Response({
        "emotions": emotion_counts,
        "most_frequent_mood": most_frequent_mood,
        "most_frequent_detailed_mood": most_frequent_detailed_mood,
    })
