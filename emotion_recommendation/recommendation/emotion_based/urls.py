# emotion_based/urls.py

from django.urls import path
from .views import recommend_movies_and_music, recommendation_result_view

#app_name = "emotion_based" -> 추천 namespace랑 안 맞음
app_name = "recommendations"  # mypage.html에서 쓰는 거랑 맞춰줘야 됨


urlpatterns = [
    # path("recommend/", recommend_movies_and_music, name="emotion_recommend"),
    path('recommendations/<int:user_id>/', recommendation_result_view, name='recommendation_result'),
    path("api/recommendations/emotion-based/", recommend_movies_and_music),
]
