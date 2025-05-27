from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from .models import UserProfile
from .serializers import *
from .services import verify_access_token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import requests

class UserProfileGetView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or malformed'}, status=401)
        token = auth_header.split(' ')[1]

        try:
            user_id = verify_access_token(token)
            profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class UserProfileUpdateView(APIView):
    def patch(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or malformed'}, status=401)
        token = auth_header.split(' ')[1]

        try:
            user_id = verify_access_token(token)
        except Exception as e:
            return Response({'detail': str(e)}, status=401)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(user).data)
        else:
            return Response(serializer.errors, status=400)


class UserCreateInternalView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user_id": user.id}, status=201)

class UserRetrieveInternalView(APIView):
    def get(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

