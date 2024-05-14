from django import forms
from django.forms import ValidationError
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser


class LoginForm(forms.Form):
    account = forms.CharField(required=True, label="會員帳號")
    password = forms.CharField(
        required=True, label="會員密碼", widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"


class RegistrationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = CustomUser  # this is the "YourCustomUser" that you imported at the top of the file
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(
                "Can't create User without committing to database"
            )
        user = CustomUser.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
        )
        return user
