from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django 세팅 모듈 경로 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')

# app이라는 이름으로 Celery 인스턴스 생성
app = Celery('notification_service')

# settings.py에서 CELERY로 시작하는 항목 읽어옴
app.config_from_object('django.conf:settings', namespace='CELERY')

# 모든 Django 앱에서 tasks.py 자동 등록
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
