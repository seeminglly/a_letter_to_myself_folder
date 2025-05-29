# routine_service/routine_service/urls.py ← 메인 URLconf 역할 수행하게 수정

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('routine.urls')),  # ✅ routine/urls.py에 실제 라우팅 로직 있음
]
