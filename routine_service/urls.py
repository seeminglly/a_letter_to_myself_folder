from django.urls import path
from . import views

app_name = 'routine_service'

urlpatterns = [
    path('api/routines/', views.get_routine_events, name='get_routine_events'),
    path('routine/', views.save_routine, name='save_routine'), # ✅ 여기에 name='save_routine' 있어야 함
    path('routine/delete/<int:pk>/', views.delete_routine, name='delete_routine'),
]