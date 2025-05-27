from django.db import models
from django.contrib.auth.models import User

class LetterRoutine(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="routines")
    title = models.CharField(max_length=200, default="편지 루틴") #루틴이름
    routine_type = models.CharField(max_length=10, choices=[('weekly', '매주'), ('monthly', '매월')], null=True, blank=True) # ✅ 빈 값 허용)
    day_of_week = models.CharField(null=True, blank=True, max_length=20)  # 매주의 경우 요일 저장
    day_of_month = models.IntegerField(null=True, blank=True)
    time = models.TimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.routine_type} ({self.day_of_week} {self.time})"


class SpecialDateRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 사용자와 연결
    name = models.CharField(max_length=255) # 기념일 이름 (ex. 생일, 결혼기념일 등)
    date = models.DateField() # 기념일 날짜

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.date})"