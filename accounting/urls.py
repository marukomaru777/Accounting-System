from django.urls import path
from . import views

urlpatterns = [
    path("detail", views.detail, name="detail"),
    path("login", views.login, name="login"),
    path("registration", views.registration, name="registration"),
    path("chkAcc", views.chkAcc, name="chkAcc"),
]
