from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("detail", views.detail, name="detail"),
    path("post/getDetail", views.getDetail, name="getDetail"),
    path("post/getSumDetail", views.getSumDetail, name="getSumDetail"),
    path("post/data", views.data, name="data"),
    path("post/getCategory", views.getCategory, name="getCategory"),
    path("post/delExpense", views.delExpense, name="delExpense"),
    path("post/getEditExpense", views.getEditExpense, name="getEditExpense"),
]
