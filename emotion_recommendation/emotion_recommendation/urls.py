# emotion_recommendation/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/recommendations/', include('recommendation.urls', namespace='recommendations')),
  # ✅ 전체 라우팅은 여기에 통합
]
