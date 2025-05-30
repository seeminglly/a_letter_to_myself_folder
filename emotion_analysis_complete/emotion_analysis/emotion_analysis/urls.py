from django.contrib import admin
from django.urls import path, include

from emotions.views import reanalyze_all_emotions
from emotions import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/emotions/analyze/", reanalyze_all_emotions),
    path("api/letters/", views.dummy_letters_view),
]

