# commons/urls.py

from django.urls import path
from . import views

app_name = "commons"  # 선택사항: 네임스페이스를 사용할 경우 필요

urlpatterns = [
    path("", views.home, name="home"),  # 예: index.html을 렌더링하는 뷰
]
