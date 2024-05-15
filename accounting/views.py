from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.shortcuts import redirect
from .forms import ExpenseForm
from accounting.func import *
from django.http import JsonResponse
from django.forms import ValidationError
from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from collections import defaultdict


def get_month_range(date_str):
    date = datetime.strptime(date_str, "%Y-%m")
    year = date.year
    month = date.month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    return [start_date, end_date]


# Create your views here.
class DetailView(LoginRequiredMixin, ListView):
    model = Expenses
    template_name = "detail.html"
    context_object_name = "expense_list"
    paginate_by = 20
    extra_context = {
        "pagination_url": "accounting:DetailView",
        "namne": "a",
        "is_paginated": True,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expenses = self.get_queryset()

        grouped_expenses = defaultdict(list)
        for expense in expenses:
            grouped_expenses[expense.e_date].append(expense)

        sorted_grouped_expenses = dict(sorted(grouped_expenses.items(), reverse=True))

        context["grouped_expenses"] = sorted_grouped_expenses
        context["summary_data"] = self.get_summary()
        return context

    def get_queryset(self):
        queryset = (
            Expenses.objects.select_related("category")
            .filter(
                username=self.request.user.username,
                e_date__range=get_month_range(datetime.now().strftime("%Y-%m")),
            )
            .order_by("-e_date")  # 按日期排序
        )
        return queryset

    def get_summary(self):
        # Aggregate expenses for each category and expense type
        category_summary = (
            Expenses.objects.filter(
                username=self.request.user.username,
                e_date__range=get_month_range(datetime.now().strftime("%Y-%m")),
            )
            .values("category__c_name", "e_type")
            .annotate(category_total=Sum("e_amount"))
        )

        # Further aggregate category totals for each expense type
        summary_data = {}
        for item in category_summary:
            e_type = item["e_type"]
            category_name = item["category__c_name"]
            category_total = item["category_total"]

            if e_type not in summary_data:
                summary_data[e_type] = {"total_spent": 0, "categories": {}}

            summary_data[e_type]["total_spent"] += category_total

            if category_name not in summary_data[e_type]["categories"]:
                summary_data[e_type]["categories"][category_name] = 0

            summary_data[e_type]["categories"][category_name] += category_total

        # Format the total spent for each category within each expense type
        for e_type, data in summary_data.items():
            data["total_spent"] = format(int(data["total_spent"]), ",")
            for category_name, total_spent in data["categories"].items():
                data["categories"][category_name] = format(int(total_spent), ",")

        return summary_data

    def post(self, request):
        try:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                SaveExpense(form.cleaned_data)
                return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "errors": str(e)})


def data(request):
    if "user" in request.session:
        current_user = request.session["user"]
        param = {"current_user": current_user}
        return render(request, "data.html", param)
    else:
        return redirect("user:login")


def index(request):
    if "user" in request.session:
        current_user = request.session["user"]
        param = {"current_user": current_user}
        return render(request, "detail.html", param)
    else:
        return redirect("user:login")


def getDetail(request):
    try:
        if request.method == "POST":
            detail = GetExpenses(
                request.POST.get("current_user"), request.POST.get("selected_date")
            )
            return JsonResponse({"success": True, "result": detail})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})


def getEditExpense(request):
    try:
        if request.method == "POST":
            detail = GetEditExpense(
                request.POST.get("current_user"), request.POST.get("e_id")
            )
            return JsonResponse({"success": True, "result": detail})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})


def getSumDetail(request):
    try:
        if request.method == "POST":
            sum_detail = GetSumExpenses(
                request.POST.get("current_user"), request.POST.get("selected_date")
            )
            return JsonResponse({"success": True, "result": sum_detail})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})


def getCategory(request):
    try:
        if request.method == "POST":
            category = GetCategory(request.POST.get("current_user"))
            return JsonResponse({"success": True, "result": category})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})


def delExpense(request):
    try:
        if request.method == "POST":
            DeleteExpense(request.POST.get("e_id"), request.POST.get("current_user"))
            return JsonResponse({"success": True, "result": "刪除成功"})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})
