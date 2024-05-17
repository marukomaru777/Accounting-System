from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
from django.db import transaction
from accounting.models import Category
from users.models import CustomUser, UserConfirmString
from django.conf import settings
import pytz
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def index(request):
    if request.user.is_authenticated:
        current_date = datetime.now().strftime("%Y-%m")
        redirect_url = reverse("accounting:detail", kwargs={"date": current_date})
        return redirect(redirect_url)
    else:
        return redirect("users:login")


class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    # 檢查密碼
    def post(self, request):
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                # Redirect to a success page.
                return JsonResponse({"success": True})
            else:
                # Return an 'invalid login' error message.
                raise Exception("帳號或密碼錯誤")
        except Exception as e:
            return JsonResponse({"success": False, "errors": "{}".format(e)})


class RegistrationView(View):
    def get(self, request):
        return render(request, "registration.html")

    # 註冊並發送確認信
    def post(self, request):
        try:
            form = RegistrationForm(data=request.POST)
            if form.is_valid():
                with transaction.atomic():
                    form.save()
                    model = form.cleaned_data
                    user = CustomUser.objects.get(username=model["username"])
                    now = datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    code = hash(model["username"] + now)
                    UserConfirmString.objects.create(code=code, username=user)
                    context = {
                        "email": user.email,
                        "confirm_url": "{}/users/confirm/?code={}".format(
                            settings.WEB_URL, code
                        ),
                        "confirm_days": settings.CONFIRM_DAYS,
                    }
                    text_content = """
                            感謝註冊 I Need Money，祝您早日財富自由，不要屈服於資本主義！
                            如果您看到這則訊息，代表您的email不提供HTML功能，請聯絡管理員，謝謝！
                            """
                    msg_html = render_to_string("signup-mail.html", context)
                    user.email_user(
                        "I Need Money 帳號驗證",
                        text_content,
                        settings.EMAIL_HOST_USER,
                        msg_html,
                    )
                    return JsonResponse({"success": True})
            else:
                raise Exception("帳號已經存在 請重新登入")
        except Exception as e:
            return JsonResponse({"success": False, "errors": "{}".format(e)})


# 驗證頁面
class ConfirmRegistration(View):
    def get(self, request):
        try:
            code = request.GET.get("code", None)
            user_confirm = UserConfirmString.objects.filter(Q(code=code)).first()
            if not user_confirm:
                message = "註冊連結不存在"
            else:
                with transaction.atomic():
                    create_time = user_confirm.create_time
                    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
                    if now > create_time + timedelta(days=settings.CONFIRM_DAYS):
                        user_confirm.username.delete()
                        message = "郵件已過期，請重新註冊"
                    else:
                        user_confirm.username.is_active = True
                        user_confirm.username.save()

                        expense_list = ["飲食", "繳費", "日常", "購物", "娛樂", "其他"]
                        income_list = ["薪水", "獎金", "兼職", "投資", "零用錢", "其他"]
                        for i in income_list:
                            Category.objects.create(
                                username=user_confirm.username,
                                c_type="+",
                                c_name=i,
                            )
                        for i in expense_list:
                            Category.objects.create(
                                username=user_confirm.username,
                                c_type="-",
                                c_name=i,
                            )

                        user_confirm.delete()
                        message = "註冊完成，請登入"
        except Exception as e:
            message = "系統發生錯誤，請聯絡管理員"
        return render(request, "confirm.html", {"message": message})


class InfoView(LoginRequiredMixin, TemplateView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = "user-info.html"  # 重寫模板名字

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 重寫get_context_data方法

        context["user_info"] = self.get_user_info()
        return context

    # 取得使用者資料
    def get_user_info(self):
        data = (
            CustomUser.objects.filter(
                username=self.request.user.username,
            )
            .annotate(name_value=Coalesce("name", Value("")))
            .first()
        )
        return data


# api


# 變更使用者密碼
@login_required
def changePassword(request):
    try:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                if request.POST["old_password"] == request.POST["new_password1"]:
                    return JsonResponse(
                        {
                            "success": False,
                            "errors": "新密碼不可與舊密碼一致",
                        }
                    )
                user = form.save()
                update_session_auth_hash(request, user)
                return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "errors": "{}".format(e)})
    return JsonResponse({"success": False, "errors": "舊密碼錯誤"})


# 變更使用者資料
@login_required
def saveUser(request):
    try:
        if request.method == "POST":
            user = CustomUser.objects.get(username=request.user.username)
            with transaction.atomic():
                user.email = request.POST["email"]
                user.name = request.POST["name"]
                user.save()
                return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


# 刪除使用者
@login_required
def delUser(request):
    try:
        if request.method == "POST":
            with transaction.atomic():
                user = CustomUser.objects.get(username=request.user.username)
                user.delete()
                return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


# 登出
@login_required
def logout_view(request):
    logout(request)
    return redirect("index")


# 檢查帳號是否存在
def chkAcc(request):
    try:
        if request.method == "POST":
            if CustomUser.objects.filter(username=request.POST["username"]).exists():
                return JsonResponse(
                    {"success": False, "errors": "帳號已經存在 請重新登入!"}
                )
            else:
                return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
