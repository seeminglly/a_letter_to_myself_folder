import requests
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.http import JsonResponse 

#마이크로서비스
#from letters.models import Letters  
#모놀리식일때
from .jwt_utils import *
from .services import create_user_in_user_service
from .serializers import *
from .models import User
#from emotions.utils import analyze_emotion_for_letter -> 서비스 따로 돌릴 때 경로
#모놀리식으로 실행시킬 때 경로
import requests

# 임시 메모리 저장소 (프로덕션에서는 Redis 등 사용)
REFRESH_TOKEN_STORE = {}



#클라이언트 API

class SignupApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        try:
            create_user_in_user_service(user.id, username, email)
        except Exception as e:
            user.delete()
            return Response({"detail": "Failed to create profile in user service"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Signup successful"}, status=status.HTTP_201_CREATED)

class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            access = create_access_token(user.id)
            refresh = create_refresh_token(user.id)
            REFRESH_TOKEN_STORE[refresh] = user.id

            response = JsonResponse({
                "detail": "Login successful",
                "access": access,
                "refresh": refresh,
            })
            response.set_cookie("access", access, httponly=True)
            response.set_cookie("refresh", refresh, httponly=True)
            return response
        return Response({"error": "Invalid credentials"}, status=401)


class LogoutApiView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh in REFRESH_TOKEN_STORE:
            del REFRESH_TOKEN_STORE[refresh]
        return Response({"message": "Logged out successfully"}, status=200)




class MypageApiView(APIView):
    def get(self, request):
        access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not access_token:
            return Response({"error": "Unauthorized"}, status=401)

        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            response = requests.get("http://localhost:8002/user/internal/get/", headers=headers) # 개발환경
            if response.status_code == 200:
                return Response(response.json(), status=200)
            else:
                return Response({"error": "Failed to retrieve user profile"}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

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