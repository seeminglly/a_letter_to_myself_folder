import json
from emotion_recommendation.recommendation.emotion_based.views import split_recommendations
from user.models import UserProfile
from django.shortcuts import render,get_object_or_404
import requests
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import openai
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.views import View

from .forms import SignupForm, LoginForm
from django.shortcuts import render
from collections import Counter
#마이크로서비스
#from letters.models import Letters  
#모놀리식일때
from letters_service.letters.models import Letter
import os
from dotenv import load_dotenv
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from .jwt_utils import *
from .services import create_user_in_user_service
from .serializers import *
from .models import User
#from emotions.utils import analyze_emotion_for_letter -> 서비스 따로 돌릴 때 경로
#모놀리식으로 실행시킬 때 경로
from emotion_analysis.emotions.utils import analyze_emotion_for_letter
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import requests

# 임시 메모리 저장소 (프로덕션에서는 Redis 등 사용)
REFRESH_TOKEN_STORE = {}



#클라이언트 API

class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "authentication/signup.html", {"form": form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists')
                return render(request, "authentication/signup.html", {"form": form})

            user = User.objects.create_user(username=username, email=email, password=password)

            try:
                create_user_in_user_service(username, email)
            except Exception as e:
                user.delete()  # 롤백
                form.add_error(None, 'Failed to create profile in user service')
                return render(request, "authentication/signup.html", {"form": form})

            return redirect("authentication:login")
        return render(request, "authentication/signup.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "authentication/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                access = create_access_token(user.id)
                refresh = create_refresh_token(user.id)
                REFRESH_TOKEN_STORE[refresh] = user.id

                login(request, user)

                response = redirect("home")  # 성공시 리디렉션
                response.set_cookie("access", access, httponly=True, samesite='Lax')
                response.set_cookie("refresh", refresh, httponly=True, samesite='Lax')
                return response
            else:
                return render(request, "authentication/login.html", {
                    "form": form,
                    "error": "Invalid credentials"
                })
        return render(request, "authentication/login.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        refresh = request.COOKIES.get("refresh")
        if refresh in REFRESH_TOKEN_STORE:
            del REFRESH_TOKEN_STORE[refresh]

        logout(request)
        response = redirect("home")
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response




class MypageView(APIView):
    def get(self, request):
        access_token = request.COOKIES.get("access")
        if not access_token:
            return redirect('authentication:login')

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
                return render(request, "authentication/mypage.html", context)
            else:
                return render(request, "authentication/mypage.html", {"error": "프로필 정보를 불러올 수 없습니다."})
        except Exception as e:
            return render(request, "authentication/mypage.html", {"error": str(e)})

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
            return Response({'detail': 'Invalid token'}, status=401)