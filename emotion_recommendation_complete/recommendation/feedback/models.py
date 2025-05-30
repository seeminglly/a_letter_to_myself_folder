# feedback/models.py
from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    FEEDBACK_CHOICES = [('like', '좋아요'), ('dislike', '별로예요')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_title = models.CharField(max_length=255)
    item_type = models.CharField(max_length=50)
    feedback = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_title} ({self.feedback})"
