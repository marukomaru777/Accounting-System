from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("detail", views.detail, name="detail"),
    path("logout", views.logout, name="logout"),
    path("login", views.login, name="login"),
    path("registration", views.registration, name="registration"),
    path("chkAcc", views.chkAcc, name="chkAcc"),
    path("getDetail", views.getDetail, name="getDetail"),
    path("getSumDetail", views.getSumDetail, name="getSumDetail"),
]
