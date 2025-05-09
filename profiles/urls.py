from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('update/', views.update_profile, name='update_profile'),
    
]
