from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import FormView
from .forms import LoginForm
from .models import User

# Create your views here.


def index(request):
    return render(request, "index.html", {"test": "123"})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():  # 表單驗證過跳轉login頁面
            return HttpResponseRedirect("/accounting/login")
    else:
        form = LoginForm()  # 給予空的表單
    return render(request, "login.html", {"form": form})  # 進行渲染


def registration(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():  # 表單驗證過跳轉login頁面
            return HttpResponseRedirect("/accounting/registration")
    else:
        form = LoginForm()  # 給予空的表單
    return render(request, "registration.html", {"form": form})  # 進行渲染
