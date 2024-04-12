from django import forms
from django.forms import ValidationError
from .models import User


class LoginForm(forms.Form):
    account = forms.CharField(required=True, label="會員帳號")
    password = forms.CharField(
        required=True, label="會員密碼", widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"


class RegistrationForm(forms.Form):
    account = forms.EmailField(required=True, label="會員帳號")
    password = forms.CharField(
        required=True, label="密碼", widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        required=True, label="確認密碼", widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_account(self):
        account = self.cleaned_data["account"]
        if User.objects.filter(account=account).exists():
            raise ValidationError("帳號已經存在 請重新登入")
        return account

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # 检查密码长度是否大于等于6
        if len(password) < 7 and (
            not any(char.isdigit() for char in password)
            or not any(char.isalpha() for char in password)
        ):
            raise ValidationError(
                "密碼需介於 8-16 碼需有 1 個以上英文字且有 1 個以上數字"
            )
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("密碼 與 確認密碼 不一致")

        return confirm_password
