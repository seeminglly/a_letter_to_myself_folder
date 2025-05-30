from celery import Celery
from celery.schedules import crontab
from schedule.tasks import send_letter_reminders
from celery import shared_task
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler_service.settings')

app = Celery('scheduler_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'Asia/Seoul'
app.conf.enable_utc = False

# Celery Beat 주기 설정
app.conf.beat_schedule = {
    'send-routine-reminder-every-minute': {
        'task': 'schedule.tasks.send_letter_reminders',
        'schedule': crontab(minute='*/1'),
    },
}
