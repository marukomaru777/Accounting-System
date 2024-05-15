from django.urls import path, re_path
from . import views

from accounting.views import DetailView

app_name = "accounting"  # app namespace

urlpatterns = [
    # path("detail", DetailView.as_view(), name="detail"),
    re_path(
        r"^detail/(?P<date>[0-9]{4}-?[0-9]{2})/$",
        DetailView.as_view(),
        name="detail",
    ),
    path("api/getCategory", views.getCategory, name="getCategory"),
    path("api/delExpense", views.delExpense, name="delExpense"),
    path("api/getEditExpense", views.getEditExpense, name="getEditExpense"),
    path("api/saveExpense", views.saveExpense, name="saveExpense"),
]
