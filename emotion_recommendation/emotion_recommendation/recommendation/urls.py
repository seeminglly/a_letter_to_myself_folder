# recommendation/urls.py

from django.urls import path
from .emotion_based.views import recommend_movies_and_music
from .feedback.views import save_feedback
app_name = 'recommendations' 

urlpatterns = [
    path("emotion-based/", recommend_movies_and_music, name="emotion_recommend"),
    path("feedback/", save_feedback, name="save_feedback"),
]
