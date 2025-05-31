from django.urls import path
from .views import *


app_name = 'user'

from .views import UserProfileGetView, UserProfileUpdateView, UserCreateInternalView, UserRetrieveInternalView


app_name = "profiles"

urlpatterns = [
    # 클라이언트 API
    path('profile/update/', UserProfileUpdateView.as_view(), name='update_profile'), # 요청 데이터 : 토큰, 내부 => accounts에게 토큰 유효성 검사 위임
    
    # 내부 서비스 API

    # 요청 데이터로 토큰 전송 > accounts에게 받은 토큰의 유효성 검사 위임 > 정상 - 사용자 프로필 정보 전송
    # accounts 마이페이지 요청 처리 : 요청 데이터 - 토큰, 내부 > accounts 에게 토큰 유효성 검사 위임 >> 사용자 프로필 데이터 전송
    path('internal/get/', UserProfileGetView.as_view(), name='get_profile'),
    path('internal/users/', UserCreateInternalView.as_view(), name='internal_create_user'), # accounts 회원가입 요청 > 대신 처리
]
