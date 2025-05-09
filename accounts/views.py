import json
from recommendations.views import split_recommendations
from profiles.models import Profile, UserProfile
from django.shortcuts import render,get_object_or_404
import requests
# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import openai
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from commons.forms import UserForm

from django.shortcuts import render
from collections import Counter

from letters.models import Letters  
import os
from dotenv import load_dotenv
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from emotions.utils import analyze_emotion_for_letter
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import re  # 상단에 import 추가


# 사용자 관리
# Create your views here.
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'accounts/login.html', {'error': '아이디 또는 비밀번호가 틀렸습니다.'})
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'account/signup.html', {'form': form})
    else:
        form = UserForm()

    return render(request, 'accounts/signup.html', {'form': form})



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reanalyze_all_emotions(request):
    user = request.user
    letters = Letters.objects.filter(user=user)

    for letter in letters:
        analyze_emotion_for_letter(letter)

 # 분석이 끝난 후 마이페이지로 리디렉션
    return redirect("commons:mypage")   


@api_view(["POST"])
def generate_comforting_message(request):
    """상위 감정(mood)에 맞는 위로의 말 생성"""

    mood = request.data.get("mood") or request.data.get("emotion")   # '기쁨', '슬픔' 등

    comfort_prompts = {
        "기쁨": "당신의 행복한 순간을 함께 나눌 수 있어 기뻐요. 그 기쁨이 오래 지속되길 바라요!",
        "슬픔": "슬픈 날에는 울어도 괜찮아요. 당신의 감정을 있는 그대로 받아들여 주세요. 저는 당신을 응원해요.",
        "분노": "화나는 감정을 느끼는 건 당연해요. 잠시 숨을 고르고, 천천히 생각을 정리해봐요.",
        "불안": "불안한 마음은 누구에게나 찾아와요. 당신은 잘 해내고 있어요. 천천히, 차분히 앞으로 나아가요.",
        "사랑": "사랑하는 마음은 참 소중해요. 그 따뜻한 마음이 더 많은 사람에게 전해지기를 바라요.",
        "중립": "감정이 특별히 떠오르지 않는 날도 있어요. 그런 날엔 그저 편안함 속에 머물러도 좋아요."
    }

    message = comfort_prompts.get(mood, "당신의 감정을 이해하고 싶어요. 편하게 이야기해 주세요.")
    return Response({"comfort_message": message})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_emotion_summary(request):
    user = request.user
    letters = Letters.objects.filter(user=user)

    emotion_list = [letter.mood for letter in letters if letter.mood]
    detailed_list = [letter.detailed_mood for letter in letters if letter.detailed_mood]  

    from collections import Counter
    emotion_counts = dict(Counter(emotion_list))
    detailed_counts = dict(Counter(detailed_list))

    most_frequent_mood = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
    most_frequent_detailed_mood = max(detailed_counts.items(), key=lambda x: x[1])[0] if detailed_counts else None

    BASE_URL = "http://127.0.0.1:8000/commons"
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }

    # ✅ comfort_message 요청은 단 한 번, 예외도 전체 감싸기
    try:
        if most_frequent_mood:
            msg_res = requests.post(
                f"{BASE_URL}/api/emotions/message/",
                headers=headers,
                json={"mood": most_frequent_mood}
            )
            comfort_message = msg_res.json().get("comfort_message", "감정 기반 메시지를 찾을 수 없습니다.")
        else:
            comfort_message = "감정이 분석되지 않았습니다. 편지를 먼저 작성해보세요."
    except Exception as e:
        print("❌ comfort message 오류:", e)
        comfort_message = "감정 기반 메세지를 불러올 수 없습니다."

    # ✅ 추천 API 호출
    try:
        recommend_res = requests.post(
            f"{BASE_URL}/api/recommendations/emotion-based/",
            headers=headers,
            cookies=request.COOKIES
        )
        recommendations = recommend_res.json().get("recommendations", "추천 결과를 찾을 수 없습니다.")
    except Exception as e:
        print("❌ 추천 오류:", e)
        recommendations = "추천 결과를 불러올 수 없습니다."

    return Response({
        "emotions": emotion_counts,
        "most_frequent_mood": most_frequent_mood,
        "most_frequent_detailed_mood": most_frequent_detailed_mood,
        "comfort_message": comfort_message,
        "recommendations": recommendations,
    })



@login_required
def mypage(request):
    user = request.user
    most_frequent_detailed_mood = None  # ✅ 기본값 설정

    # 🔗 내부 API 통합 호출
    BASE_URL = "http://127.0.0.1:8000/commons"  # 배포 시 도메인으로 변경
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/emotion-summary/",
            cookies=request.COOKIES  # 세션 인증 유지
        )
        if response.status_code == 200:
            data = response.json()
            emotions = data.get("emotions", {})
            most_frequent_mood = data.get("most_frequent_mood")
            most_frequent_detailed_mood = data.get("most_frequent_detailed_mood")  # ✅ 추가
            comfort_message = data.get("comfort_message")
            recommendations = data.get("recommendations")
        else:
            emotions = {}
            most_frequent_mood = None
            comfort_message = "감정 메시지를 불러오지 못했습니다."
            recommendations = "추천 결과를 불러오지 못했습니다."
    except Exception as e:
        emotions = {}
        most_frequent_mood = None
        comfort_message = "감정 메시지를 불러오지 못했습니다."
        recommendations = "추천 결과를 불러오지 못했습니다."
    # 사용자 정보
    profile, _ = Profile.objects.get_or_create(user=user)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    letter_count = user.letters.count()
    routine_count = user.routines.count()

    movie_lines, music_lines = split_recommendations(recommendations)


    context = {
        "user": user,
        "user_profile": user_profile,
        "profile": profile,
        "emotions": json.dumps(emotions),
        "mood_counts": emotions,
        "most_frequent_mood": most_frequent_mood,
        "most_frequent_detailed_mood": most_frequent_detailed_mood,
        "comfort_message": comfort_message,
        "recommendations": recommendations,
        "letter_count": letter_count,
        "routine_count": routine_count,
        "recommendation_lines": recommendations.splitlines() if recommendations else [],
        "movie_lines": movie_lines,
        "music_lines": music_lines,

    }

    return render(request, 'accounts/mypage.html', context)
