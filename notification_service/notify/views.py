from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from notify.tasks import send_notification
import json

@csrf_exempt
@require_POST
def email_notification_api(request):
    try:
        data = json.loads(request.body)
        email = data["email"]
        username = data["username"]
        time = data["time"]

        send_notification.delay(email, username, time)
        return JsonResponse({"status": "success", "message": f"알림 전송 요청 완료 → {email}"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


def test_notification_api(request):
    return JsonResponse({'message': 'Notification sent!'})