from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_notification(user_email, username, routine_time):
    subject = "편지 작성 알림"
    message = f"{username}님! 오늘은 편지를 작성할 날입니다. ({routine_time})"
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False
    )
    print(f"편지 알림 전송 완료 → {user_email}")