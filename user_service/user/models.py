from django.db import models

class UserProfile(models.Model):
    user_id = models.IntegerField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    birthday = models.DateField(blank=True, null=True)
    blog_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UserProfile ({self.user_id})"
