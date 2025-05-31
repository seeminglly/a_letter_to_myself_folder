from django.http import JsonResponse
def view(request): return JsonResponse({'message': 'ok'})