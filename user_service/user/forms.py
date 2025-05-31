from django import forms
from user.models import UserProfile
#from django.contrib.auth.models import User #UserForm에서 model = User 가 인식
from django.contrib.auth import get_user_model

User = get_user_model()
class UserForm(forms.ModelForm): #회원가입 폼에 사용
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ProfileForm(forms.ModelForm): # 프로필 수정 필드 추가
    password = None
    class Meta:
        model = UserProfile
        fields = ["nickname", "bio", "birthday", "blog_url"]

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]
