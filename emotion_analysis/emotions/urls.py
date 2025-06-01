# emotion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.reanalyze_all_emotions, name="reanalyze_all"),
    path("summary/", views.user_emotion_summary, name="emotion_summary"),
    path("api/emotions/analyze/", views.reanalyze_all_emotions),

]
