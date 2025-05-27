from django import forms
from .models import User

class SignupForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
