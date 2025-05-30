
import json
from emotion_recommendation.recommendation.emotion_based.views import split_recommendations
from user.models import Profile, UserProfile
from django.shortcuts import render,get_object_or_404
import requests
# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import openai
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from django.shortcuts import redirect
from user.forms import UserForm

=======
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.views import View

from .forms import SignupForm, LoginForm

from django.shortcuts import render
from collections import Counter


from letters.models import Letters  
#마이크로서비스
#from letters.models import Letters  
#모놀리식일때
from letters_service.letters.models import Letter
import os
from dotenv import load_dotenv
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response

from .jwt_utils import *
from .services import create_user_in_user_service
from .serializers import *
from .models import User
#from emotions.utils import analyze_emotion_for_letter -> 서비스 따로 돌릴 때 경로
#모놀리식으로 실행시킬 때 경로
from emotion_analysis.emotions.utils import analyze_emotion_for_letter
from django.views.decorators.http import require_POST
from django.http import JsonResponse
<<<<<<< HEAD
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, logout
from django.contrib.auth.hashers import make_password, check_password
from django.views import View
from .forms import SignupForm, LoginForm
from .jwt_utils import *
from .services import create_user_in_user_service
from .models import User
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

=======
import requests
>>>>>>> c20f728 (api 정리)

# 임시 메모리 저장소 (프로덕션에서는 Redis 등 사용)
REFRESH_TOKEN_STORE = {}


<<<<<<< HEAD
=======

#클라이언트 API

>>>>>>> c20f728 (api 정리)
class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "accounts/signup.html", {"form": form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists')
                return render(request, "accounts/signup.html", {"form": form})

            user = User.objects.create_user(username=username, email=email, password=password)

            try:
                create_user_in_user_service(username, email)
            except Exception as e:
                user.delete()  # 롤백
                form.add_error(None, 'Failed to create profile in user service')
                return render(request, "accounts/signup.html", {"form": form})

            return redirect("accounts:login")
        return render(request, "accounts/signup.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "accounts/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        REFRESH_TOKEN_STORE[refresh] = user.id
        return Response({'access': access, 'refresh': refresh})


class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh = request.data.get('refresh')
        if refresh in REFRESH_TOKEN_STORE:
            del REFRESH_TOKEN_STORE[refresh]
        return Response(status=204)




class MypageView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access")
        if not access_token:
            return redirect('accounts:login')

        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            response = requests.get("http://localhost:8000/user/internal/get/", headers=headers) # 경로 추후 변경 필요
            if response.status_code == 200:
                profile_data = response.json()
                context = {
                    "user": {
                        "username": profile_data.get("username"),
                        "email": profile_data.get("email"),
                    },
                    "user_profile": {
                        "profile_picture": {"url": "/static/images/basicprofile.png"},  # 임시 기본 이미지 처리
                    },
                    "profile": {
                        "nickname": profile_data.get("nickname", ""),
                        "bio": profile_data.get("bio", ""),
                        "birthday": profile_data.get("birthday", ""),
                        "blog_url": profile_data.get("blog_url", ""),
                    }
                }
                return render(request, "accounts/mypage.html", context)
            else:
                return render(request, "accounts/mypage.html", {"error": "프로필 정보를 불러올 수 없습니다."})
        except Exception as e:
            return render(request, "accounts/mypage.html", {"error": str(e)})

# 내부 서비스 API   

class TokenRefreshView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']
        try:
            user_id = verify_token(refresh, token_type='refresh')
            if REFRESH_TOKEN_STORE.get(refresh) != user_id:
                return Response({'detail': 'Invalid refresh token'}, status=401)
            access = create_access_token(user_id)
            return Response({'access': access})
        except ExpiredSignatureError:
            return Response({'detail': 'Refresh token expired'}, status=401)
        except InvalidTokenError:
            return Response({'detail': 'Invalid refresh token'}, status=401)




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
    # BASE_URL = "http://127.0.0.1:8000/commons"  # 배포 시 도메인으로 변경
    BASE_URL = "http://127.0.0.1:8000/emotion"
    try:
        # response = requests.get(
        #     f"{BASE_URL}/api/user/emotion-summary/",
        #     cookies=request.COOKIES  # 세션 인증 유지
        # )
        
        response = requests.get(
            f"{BASE_URL}/summary/",
            cookies=request.COOKIES
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

class TokenVerifyInternalView(APIView):
    def post(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        try:
            user_id = verify_token(token)
            return Response({'user_id': user_id})
        except ExpiredSignatureError:
            return Response({'detail': 'Token expired'}, status=401)
        except InvalidTokenError:
<<<<<<< HEAD
            return Response({'detail': 'Invalid token'}, status=401)




class MypageView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access")
        if not access_token:
            return redirect('accounts:login')

        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            response = requests.get("http://localhost:8000/user/profile/get/", headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                context = {
                    "user": {
                        "username": profile_data.get("username"),
                        "email": profile_data.get("email"),
                    },
                    "user_profile": {
                        "profile_picture": {"url": "/static/images/basicprofile.png"},  # 임시 기본 이미지 처리
                    },
                    "profile": {
                        "nickname": profile_data.get("nickname", ""),
                        "bio": profile_data.get("bio", ""),
                        "birthday": profile_data.get("birthday", ""),
                        "blog_url": profile_data.get("blog_url", ""),
                    }
                }
                return render(request, "accounts/mypage.html", context)
            else:
                return render(request, "accounts/mypage.html", {"error": "프로필 정보를 불러올 수 없습니다."})
        except Exception as e:
            return render(request, "accounts/mypage.html", {"error": str(e)})
=======
            return Response({'detail': 'Invalid token'}, status=401)
>>>>>>> c20f728 (api 정리)
