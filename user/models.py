from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os

# Create your models here.
from django.conf import settings
# Create your models here.

def profile_picture_upload_to(instance, filename):
    # 파일명을 slugify로 변환하여 안전한 문자로 만듬
    base, ext = os.path.splitext(filename)
    slugified_name = slugify(base)
    return f'profile_pics/{slugified_name}{ext}'

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=10)
    bio = models.TextField(blank=True)
    picture = models.ImageField(blank=True)
    birthday = models.DateField(auto_now=False, null=True, blank=True)
    blog_url = models.URLField(max_length = 60, blank=True)
    
    def __str__(self):
        return self.user.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ✅ 사용자와 1:1 연결
    profile_picture = models.ImageField(
    upload_to='profile_pics/',
    blank=True,
    null=True
)
 # ✅ 프로필 사진 저장

    def __str__(self):
        return self.user.username
    

    

