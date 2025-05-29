from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("schedule.urls")),  # 또는 경로를 지정해도 좋아
]
