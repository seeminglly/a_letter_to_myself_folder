import requests
from celery import shared_task
import os

# @shared_task
# def send_letter_reminders():
    
#     #현재 시간 정보 가져오기
#     from django.utils.timezone import now, localtime
#     from datetime import timedelta

#     now_dt = localtime(now()).replace(second=0, microsecond=0)
#     today = now_dt.strftime("%A") # Monday, Tuesday ...
#     current_day = now_dt.day # 1~31
#     current_time = now_dt.time()

#     # ±1분 오차 허용
#     window_start = (now_dt - timedelta(minutes=1)).time()
#     window_end = (now_dt + timedelta(minutes=1)).time()

#     print("✅ 루틴 알림 작업 실행됨!")
#     print(f"현재 시간: {current_time}")
#     print(f"알림 시간 범위: {window_start} ~ {window_end}")
#     print(f"오늘 요일: {today}, 날짜: {current_day}")

#     # 🟡 루틴 정보 API 호출 (routine-service)
#     ROUTINE_API_URL = os.getenv("ROUTINE_SERVICE_URL", "http://localhost:8003/api/routines/today/")
#     try:
#         response = requests.get(ROUTINE_API_URL)
#         if response.status_code != 200:
#             print("❌ 루틴 서비스 응답 실패:", response.status_code)
#             return
#         routines = response.json()
#     except Exception as e:
#         print("❌ 루틴 API 요청 실패:", e)
#         return

#     # 🔵 notification-service로 task 큐 전달
#     from notify.tasks import send_notification

#     for routine in routines:
#         print(f"📌 루틴 확인 → {routine}")
#         send_notification.delay(
#             routine['user_email'],
#             routine['username'],
#             routine['time']
#         )
        
        
#마이크로서비스 테스트용!!!!!!

@shared_task
def send_letter_reminders():
    print("✅ 테스트용 루틴 알림 작업 실행됨!")

    try:
        response = requests.get("http://localhost:8003/api/routines/today/")
        routines = response.json()
    except Exception as e:
        print("❌ 루틴 요청 실패:", e)
        return

    for routine in routines:
        # 여기선 큐로 보내는 대신 단순 print
        print(f"📬 예약된 루틴 → {routine['username']} | {routine['time']} | {routine['email']}")
        
def send_notification(routine):
    NOTIFICATION_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8005/notify/email/")

    try:
        response = requests.post(NOTIFICATION_URL, json={
            "email": routine.user.email,
            "username": routine.user.username,
            "time": str(routine.time)
        })
        print(f"📬 이메일 요청 완료 → {routine.user.email}, 응답 코드: {response.status_code}")
    except Exception as e:
        print("❌ 이메일 요청 실패:", e)
        