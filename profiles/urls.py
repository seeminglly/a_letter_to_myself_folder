from django.urls import path
from .views import UserProfileGetView, UserProfileUpdateView, UserCreateInternalView, UserRetrieveInternalView

urlpatterns = [
    # 클라이언트 API
    path('profile/get/', UserProfileGetView.as_view(), name='get_profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='update_profile'),

    # 내부 서비스 API
    path('internal/users/', UserCreateInternalView.as_view(), name='internal_create_user'),
    path('internal/users/<int:user_id>/', UserRetrieveInternalView.as_view(), name='internal_get_user'),
]
