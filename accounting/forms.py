from django import forms


class LoginForm(forms.forms):
    userId = forms.CharField(label="帳號", required=True)
    password = forms.CharField(label="密碼", widget=forms.PasswordInput)
