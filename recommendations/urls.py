from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path("emotion-based/", views.recommend_movies_and_music, name="emotion_recommend"),
    path("feedback/", views.save_feedback, name="save_feedback"),
]
