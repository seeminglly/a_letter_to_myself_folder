from django.urls import path
from .views import SignupView, LoginView, LogoutView, TokenRefreshView, TokenVerifyInternalView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("internal/verify/", TokenVerifyInternalView.as_view(), name="token_verify"),
]
