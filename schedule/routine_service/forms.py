from django import forms
from .models import LetterRoutine, SpecialDateRoutine

class LetterRoutineForm(forms.ModelForm):
    class Meta:
        model = LetterRoutine
        fields = ['title', 'routine_type', 'day_of_week', 'day_of_month', 'time']

class SpecialDateRoutineForm(forms.ModelForm):
    class Meta:
        model = SpecialDateRoutine #올바른 모델 참조
        fields = ["name", "date"] #필요한 필드만 포함(user 제거)