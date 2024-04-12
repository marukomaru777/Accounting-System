from django.forms import ValidationError
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views.generic import FormView
from .forms import LoginForm, RegistrationForm
from accounting.func import *
from django.http import JsonResponse

# Create your views here.
err_result = {"success": False, "errors": "系統發生錯誤，請聯絡管理員"}


def detail(request):
    return render(request, "detail.html", {"test": "123"})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = Login(form.cleaned_data)
            if not user:
                return JsonResponse(
                    {"success": False, "errors": "身份驗證失敗，帳號不存在"}
                )
            if not check_password(form.cleaned_data["password"], user.password):
                return JsonResponse(
                    {"success": False, "errors": "身份驗證失敗，密碼錯誤"}
                )
            return JsonResponse({"success": True})
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def registration(request):
    try:
        if request.method == "POST":
            form = RegistrationForm(request.POST)

            if form.is_valid():
                if Register(form.cleaned_data):
                    return JsonResponse({"success": True})
        else:
            form = RegistrationForm()
    except ValidationError as e:
        return JsonResponse({"success": False, "errors": e.message_dict})
    return render(request, "registration.html", {"form": form})


def chkAcc(request):
    try:
        if request.method == "POST":
            if IsAccExists(request.POST.get("account")):
                return JsonResponse(
                    {"success": False, "errors": "帳號已經存在 請重新登入"}
                )
            else:
                return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse(err_result)
