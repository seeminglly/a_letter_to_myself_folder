from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('update/', views.update_profile, name='update_profile'),
    
]
