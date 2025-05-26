from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from .serializers import *
from .jwt_utils import *
from .services import create_user_in_user_service
from .models import User
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


# 임시 메모리 저장소 (프로덕션에서는 Redis 등 사용)
REFRESH_TOKEN_STORE = {}


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Auth 서비스에 사용자 저장
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists'}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)

        # User 서비스에 프로필 저장 (비밀번호 제외)
        user_id = create_user_in_user_service(username, email)
        return Response({"user_id": user.id}, status=201)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=401)

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
