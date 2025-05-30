from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("notify/", include("notify.urls")),  # ✅ 앱 URL 포함
]
