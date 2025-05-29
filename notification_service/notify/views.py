from django.http import JsonResponse

def send_notification(request):
    return JsonResponse({'message': 'Notification sent!'})
