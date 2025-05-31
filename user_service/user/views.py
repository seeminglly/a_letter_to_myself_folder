from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile
from .serializers import *
from .services import verify_access_token


class UserProfileUpdateView(APIView):
    def get(self, request):
        token = request.COOKIES.get("access")
        if not token:
            return Response({"detail": "Authentication required."}, status=401)

        try:
            user_id = verify_access_token(token)
            profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def patch(self, request):
        token = request.COOKIES.get("access")
        if not token:
            return Response({"detail": "Authentication required."}, status=401)

        try:
            user_id = verify_access_token(token)
        except Exception as e:
            return Response({"detail": str(e)}, status=401)

        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=404)

        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Profile updated successfully."})
        else:
            return Response(serializer.errors, status=400)


class UserProfileGetView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or malformed'}, status=401)
        token = auth_header.split("Bearer ")[1]

        try:
            user_id = verify_access_token(token)
            profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class UserCreateInternalView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response({"user_id": profile.user_id}, status=201)
