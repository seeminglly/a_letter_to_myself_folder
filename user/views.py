from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import redirect, render

from accounts.models import User
from .models import UserProfile
from .serializers import *
from .services import verify_access_token

#클라이언트 API

class UserProfileUpdateView(APIView):
    def get(self, request):
        token = request.COOKIES.get("access")
        if not token:
            return redirect('accounts:login')

        try:
            user_id = verify_access_token(token)
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user_id=user_id)
            context = {
                'user': user,
                'profile': profile,
            }
            return render(request, 'profiles/update_profile.html', context)
        except Exception as e:
            print(f"[ERROR] {e}")
            return redirect('accounts:login')

    def post(self, request):
        token = request.COOKIES.get("access")
        if not token:
            return redirect('accounts:login')

        try:
            user_id = verify_access_token(token)
        except Exception as e:
            print(f"[ERROR] {e}")
            return redirect('accounts:login')

        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return redirect('accounts:login')

        data = request.POST.copy()
        data.update(request.FILES)

        serializer = UserProfileUpdateSerializer(profile, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return redirect('accounts:mypage')
        else:
            return render(request, 'profiles/update_profile.html', {
                'profile': profile,
                'errors': serializer.errors,
            })

# 내부 서비스 API

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
        user = serializer.save()
        return Response({"user_id": user.id}, status=201)