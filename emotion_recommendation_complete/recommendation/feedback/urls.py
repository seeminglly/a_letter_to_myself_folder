# feedback/urls.py
from django.urls import path
from .views import save_feedback

urlpatterns = [
    path('save/', save_feedback, name='save_feedback'),
]
