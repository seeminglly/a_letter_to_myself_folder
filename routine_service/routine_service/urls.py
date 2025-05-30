# routine_service/routine_service/urls.py ← 메인 URLconf 역할 수행하게 수정

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView



app_name = 'routines'

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", TemplateView.as_view(template_name="commons/index.html"), name="home"),

    path("routine/", include("routine.urls")),
]
