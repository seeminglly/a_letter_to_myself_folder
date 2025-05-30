# emotion_store_only/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.views import EmotionResultViewSet

router = DefaultRouter()
router.register(r'api/emotion-results', EmotionResultViewSet, basename='emotionresult')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
