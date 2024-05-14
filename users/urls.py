from django.urls import path
from . import views

from users.views import LoginView

urlpatterns = [
    path("logout", views.logout, name="logout"),
    # path("login", views.login, name="login"),
    path("login/", LoginView.as_view(), name="login"),
    path("registration", views.registration, name="registration"),
    path("confirm/", views.confirmRegistration),
    path("post/chkAcc", views.chkAcc, name="chkAcc"),
]
