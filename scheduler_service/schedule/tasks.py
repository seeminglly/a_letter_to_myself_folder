import requests
from celery import shared_task
import os

@shared_task
def send_letter_reminders():
    
    #현재 시간 정보 가져오기
    from django.utils.timezone import now, localtime
    from datetime import timedelta

    now_dt = localtime(now()).replace(second=0, microsecond=0)
    today = now_dt.strftime("%A") # Monday, Tuesday ...
    current_day = now_dt.day # 1~31
    current_time = now_dt.time()

    # ±1분 오차 허용
    window_start = (now_dt - timedelta(minutes=1)).time()
    window_end = (now_dt + timedelta(minutes=1)).time()

    print("✅ 루틴 알림 작업 실행됨!")
    print(f"현재 시간: {current_time}")
    print(f"알림 시간 범위: {window_start} ~ {window_end}")
    print(f"오늘 요일: {today}, 날짜: {current_day}")

    routines = LetterRoutine.objects.filter(time__range=(window_start, window_end))

    for routine in routines:
        print(f"🔍 루틴 체크: {routine.routine_type} / {routine.day_of_week} / {routine.time}")
        if routine.routine_type == 'weekly' and routine.day_of_week == today:
            send_notification(routine)
        if routine.routine_type == 'monthly' and routine.day_of_month == current_day:
            send_notification(routine)

def send_notification(routine):
    NOTIFICATION_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8000/notify/email/")

    try:
        response = requests.post(NOTIFICATION_URL, json={
            "email": routine.user.email,
            "username": routine.user.username,
            "time": str(routine.time)
        })
        print(f"📬 이메일 요청 완료 → {routine.user.email}, 응답 코드: {response.status_code}")
    except Exception as e:
        print("❌ 이메일 요청 실패:", e)