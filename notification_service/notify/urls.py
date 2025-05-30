from django.urls import path
from . import views

urlpatterns = [
    path("send/", views.test_notification_api, name="send_notification"),
    path("email/", views.email_notification_api),  # POST로 알림 요청 받는 엔드포인트

]
