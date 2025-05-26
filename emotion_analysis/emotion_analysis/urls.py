from django.contrib import admin
from django.urls import path, include

from emotions.views import reanalyze_all_emotions

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/emotions/analyze/", reanalyze_all_emotions),  # ← 이렇게 바꿔야 깔끔
]

