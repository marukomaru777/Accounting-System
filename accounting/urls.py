from django.urls import path, re_path
from . import views

from accounting.views import DetailView, CategorylView

app_name = "accounting"  # app namespace

urlpatterns = [
    # path("detail", DetailView.as_view(), name="detail"),
    re_path(
        r"^detail/(?P<date>[0-9]{4}-?[0-9]{2})/$",
        DetailView.as_view(),
        name="detail",
    ),
    path("category/", CategorylView.as_view(), name="category"),
    path("api/getCategory/", views.getCategory, name="getCategory"),
    path("api/delExpense/", views.delExpense, name="delExpense"),
    path("api/delCategory/", views.delCategory, name="delCategory"),
    path("api/getEditExpense/", views.getEditExpense, name="getEditExpense"),
    path("api/getEditCategory/", views.getEditCategory, name="getEditCategory"),
    path("api/saveExpense/", views.saveExpense, name="saveExpense"),
    path("api/saveCategory/", views.saveCategory, name="saveCategory"),
]
