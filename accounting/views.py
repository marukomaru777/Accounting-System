from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "index.html", {"test": "123"})


def login(request):
    return render(request, "login.html", {"test": 123})
