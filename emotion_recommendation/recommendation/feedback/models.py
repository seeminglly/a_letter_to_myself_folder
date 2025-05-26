# recommendation/models.py

from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20)  # 'movie' or 'music'
    item_title = models.TextField()
    feedback = models.CharField(max_length=10)  # 'like' or 'dislike'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_type} - {self.feedback}"
