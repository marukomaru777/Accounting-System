from django.shortcuts import render
from django.shortcuts import redirect
from .forms import LoginForm, RegistrationForm
from accounting.func import *
from django.http import JsonResponse
from django.forms import ValidationError

from django.views import View

class LoginView(View):

    def get(self, request):
        return render(request, "login.html")

    def post(self, request):

        form = LoginForm(request.POST)
        if form.is_valid():
            # 找尋認證過的帳號
            user = CustomUser.objects.filter(
                Q(account=form.cleaned_data["account"]) & Q(is_active=True)
            ).first()

            if not user:
                raise Exception("身份驗證失敗，帳號不存在")

            if not check_password(form.cleaned_data["password"], user.password):
                raise Exception("身份驗證失敗，密碼錯誤")

            request.session["user"] = form.cleaned_data["account"]
            return JsonResponse({"success": True})


def logout(request):
    try:
        del request.session["user"]
    except:
        return redirect("login")
    return redirect("login")


def registration(request):
    try:
        if request.method == "POST":
            form = RegistrationForm(request.POST)

            if form.is_valid():
                if not CustomUser.objects.filter(
                    Q(account=form.cleaned_data["account"])
                ).exists():
                    with transaction.atomic():
                        new_user = CustomUser(
                            account=form.cleaned_data["account"],
                            password=make_password(form.cleaned_data["password"]),
                            email=form.cleaned_data["account"],
                            is_active=False,
                        )
                        # Save the user to the database
                        new_user.save()

                        # Save the confitm string and send mail to user
                        SendRegisterMail(new_user.account, new_user.email)
                else:
                    raise Exception("帳號已經存在 請重新登入")
                    # Register(form.cleaned_data)
                return JsonResponse({"success": True})
        else:
            form = RegistrationForm()
    except ValidationError as e:
        return JsonResponse({"success": False, "errors": e.message_dict})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return render(request, "registration.html", {"form": form})


def chkAcc(request):
    try:
        if request.method == "POST":
            if IsAccExists(request.POST.get("account")):
                return JsonResponse(
                    {"success": False, "errors": "帳號已經存在 請重新登入!"}
                )
            else:
                return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


def confirmRegistration(request):
    try:
        code = request.GET.get("code", None)
        msg = ConfirmRegistration(code)
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    form = LoginForm()
    return render(request, "confirm.html", {"message": msg, "form": form})
