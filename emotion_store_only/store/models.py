from django.db import models
from django.contrib.auth.models import User

class EmotionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    letter_id = models.IntegerField(default=0)
    dominant_emotion = models.CharField(max_length=50)
    detailed_emotion = models.CharField(max_length=50)
    emotion_scores = models.JSONField()
    most_frequent_mood = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmotionResult {self.letter_id} - {self.dominant_emotion}"
