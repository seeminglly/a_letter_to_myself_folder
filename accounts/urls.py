from django.urls import path
from .views import *

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("internal/verify/", TokenVerifyInternalView.as_view(), name="token_verify"),

    path('mypage/', MypageView.as_view(), name='mypage'),
]
