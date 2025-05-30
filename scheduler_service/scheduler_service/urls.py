from django.urls import path, include

urlpatterns = [
    path("", include("schedule.urls")), # 내부 API만 씀
]
