from django.urls import path
from .views import *

app_name = "authentication"

urlpatterns = [
    #클라이언트 API
    path("signup/", SignupApiView.as_view(), name="signup"), # 내부 => user에게 사용자 생성 위임
    path("login/", LoginApiView.as_view(), name="login"),
    path("logout/", LogoutApiView.as_view(), name="logout"), 
    path('mypage/', MypageApiView.as_view(), name='mypage'), # 내부 => user에게 사용자 프로필 데이터 요청

    # 내부 서비스 API    
    path("internal/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("internal/verify/", TokenVerifyInternalView.as_view(), name="token_verify"), # user, ... 폴더에서 토큰 유효성 검사 요청

]
