from .models import CustomUser, Expenses, Category
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.db.models import Sum
from django.db import transaction
from django.db.models import Q
import calendar


def IsAccExists(account):
    return CustomUser.objects.filter(Q(account=account)).exists()


def get_month_range(date_str):
    date = datetime.strptime(date_str, "%Y-%m")
    year = date.year
    month = date.month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    return start_date, end_date


def Register(model):
    try:
        if not IsAccExists(model["account"]):
            with transaction.atomic():
                new_user = CustomUser(
                    account=model["account"],
                    user_id=model["account"],
                    password=make_password(model["password"]),
                )
                # Save the user to the database
                new_user.save()
                expense_list = ["飲食", "繳費", "日常", "購物", "娛樂", "其他"]
                income_list = ["薪水", "獎金", "兼職", "投資", "零用錢", "其他"]
                for i in income_list:
                    Category.objects.create(
                        u_account=model["account"], c_type="+", c_name=i
                    )
                for i in expense_list:
                    Category.objects.create(
                        u_account=model["account"], c_type="-", c_name=i
                    )
        else:
            raise Exception("帳號已經存在 請重新登入")
    except Exception as e:
        raise Exception("{}".format(e))


def Login(model):
    try:
        user = CustomUser.objects.filter(account=model["account"]).first()
        if not user:
            raise Exception("身份驗證失敗，帳號不存在")
        if not check_password(model["password"], user.password):
            raise Exception("身份驗證失敗，密碼錯誤")
        return user.account
    except Exception as e:
        raise Exception("{}".format(e))


def GetExpenses(acc, year_month):
    date_from, date_to = get_month_range(year_month)
    result = (
        Expenses.objects.select_related("category")
        .values("category__c_name", "e_date", "e_desc", "e_type", "e_amount")
        .filter(u_account=acc, e_date__range=[date_from, date_to])
    )
    return list(result)


def GetSumExpenses(acc, year_month):
    date_from, date_to = get_month_range(year_month)
    grouped_expenses = (
        Expenses.objects.select_related("category")
        .values("category__c_name")  # 通过外键关联的模型名加上字段名来访问相关字段
        .annotate(total_spent=Sum("e_amount"))
        .filter(u_account=acc, e_date__range=[date_from, date_to])
    )
    return list(grouped_expenses)
