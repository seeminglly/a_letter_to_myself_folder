from django.http import JsonResponse
from django.views.decorators.http import require_GET
from scheduler_service.celery import app


@require_GET
def celery_status(request):
    """
    Celery 작업 상태를 확인하는 API (내부 관리용)
    """
    i = app.control.inspect()
    stats = i.stats()

    if not stats:
        return JsonResponse({'status': 'offline'}, status=503)
    return JsonResponse({'status': 'online', 'details': stats})
