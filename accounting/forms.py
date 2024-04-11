from django import forms


class LoginForm(forms.Form):
    account = forms.CharField(label="會員帳號", required=True)
    password = forms.CharField(label="會員密碼", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
