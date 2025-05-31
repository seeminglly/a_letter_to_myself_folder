# emotion_results/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import EmotionResult
from .serializers import EmotionResultSerializer

class EmotionResultViewSet(viewsets.ModelViewSet):
    queryset = EmotionResult.objects.all()
    serializer_class = EmotionResultSerializer
    permission_classes = [AllowAny]
