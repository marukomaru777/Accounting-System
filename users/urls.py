from django.urls import path
from . import views

from users.views import LoginView, RegistrationView, ConfirmRegistration, InfoView

app_name = "users"  # app namespace

urlpatterns = [
    path("logout/", views.logout_view, name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("confirm/", ConfirmRegistration.as_view()),
    path("info/", InfoView.as_view(), name="info"),
    path("api/chkAcc/", views.chkAcc, name="chkAcc"),
    path("api/saveUser/", views.saveUser, name="saveUser"),
    path("api/changePwd/", views.changePassword, name="changePwd"),
]
