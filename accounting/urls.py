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
    path("data", views.data, name="data"),
    path("getCategory", views.getCategory, name="getCategory"),
    path("delExpense", views.delExpense, name="delExpense"),
    path("getEditExpense", views.getEditExpense, name="getEditExpense"),
    path("confirm/", views.confirmRegistration),
]
