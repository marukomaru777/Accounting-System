from django.urls import path
from . import views

from users.views import LoginView, RegistrationView, ConfirmRegistration

app_name = "users"  # app namespace

urlpatterns = [
    path("logout/", views.logout, name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("confirm/", ConfirmRegistration.as_view()),
    path("api/chkAcc/", views.chkAcc, name="chkAcc"),
]
