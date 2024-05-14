from django.urls import path
from . import views

app_name = "accounting"  # app namespace

urlpatterns = [
    path("detail", views.detail, name="detail"),
    path("api/getDetail", views.getDetail, name="getDetail"),
    path("api/getSumDetail", views.getSumDetail, name="getSumDetail"),
    path("api/data", views.data, name="data"),
    path("api/getCategory", views.getCategory, name="getCategory"),
    path("api/delExpense", views.delExpense, name="delExpense"),
    path("api/getEditExpense", views.getEditExpense, name="getEditExpense"),
]
