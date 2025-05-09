from django import forms
from .models import UserProfile, Profile

class ProfileForm(forms.ModelForm): # 프로필 수정 필드 추가
    password = None
    class Meta:
        model = Profile
        fields = ["nickname", "bio", "birthday", "blog_url"]

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]
