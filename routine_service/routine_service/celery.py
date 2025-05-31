from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Django 세팅 파일 위치 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'routine_service.settings')

app = Celery('routine_service')

# Django settings 기반 config
app.config_from_object('django.conf:settings', namespace='CELERY')

# 자동 task 모듈 탐색 (INSTALLED_APPS 기준)
app.autodiscover_tasks()

# Timezone 설정
app.conf.timezone = 'Asia/Seoul'
app.conf.enable_utc = False

# Celery Beat 주기 설정 (필요 시 수정)
app.conf.beat_schedule = {
    'send-routine-reminder-every-minute': {
        'task': 'scheduler_service.tasks.send_letter_reminders',
        'schedule': crontab(minute='*/1'),
    },
}
