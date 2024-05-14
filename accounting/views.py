from django.shortcuts import render
from django.shortcuts import redirect
from .forms import ExpenseForm
from accounting.func import *
from django.http import JsonResponse
from django.forms import ValidationError


# Create your views here.


def detail(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                form = ExpenseForm(request.POST)
                if form.is_valid():
                    SaveExpense(form.cleaned_data)
                    return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "errors": str(e)})
        else:
            param = {"form": ExpenseForm()}
        return render(request, "detail.html", param)
    else:
        return redirect("user:login")


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
