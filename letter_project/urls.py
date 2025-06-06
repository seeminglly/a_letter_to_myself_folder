"""
URL configuration for letter_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", TemplateView.as_view(template_name="commons/index.html"), name="home"),
    
    path("letters/", include("letters.urls")), #->마이크로서비스
    #모놀리식으로 실행할 때
    # path("letters/", include("letters_service.letters.urls")),

    path("routines/", include(("routine_service.urls", "routines"), namespace="routines")), # ->마이크로서비스
    #모놀리식으로 실행할 때
    # path("routines/", include(("routine_service.routine.urls", "routines"), namespace="routines")),

    path("authentication/", include("authentication.urls")),
    path("user/", include("user.urls")),
    
    path("recommendations/", include("recommendations.urls")), # ->마이크로서비스로 돌릴 때
    #모놀리식으로 돌릴 때
    # path("api/recommendations/", include(("emotion_recommendation.recommendation.urls", "recommendations"), namespace="recommendations")),
]
