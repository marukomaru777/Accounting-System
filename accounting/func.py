from accounting.models import Expenses, Category
from users.models import CustomUser, UserConfirmString
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db import transaction
from django.db.models import Q
from django.conf import settings
import calendar
import pytz


def IsAccExists(username):
    return CustomUser.objects.filter(Q(username=username) & Q(is_active=True)).exists()


def get_month_range(date_str):
    date = datetime.strptime(date_str, "%Y-%m")
    year = date.year
    month = date.month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    return start_date, end_date


def Login(model):
    try:
        user = CustomUser.objects.filter(
            Q(username=model["username"]) & Q(is_active=True)
        ).first()
        if not user:
            raise Exception("身份驗證失敗，帳號不存在")
        if not check_password(model["password"], user.password):
            raise Exception("身份驗證失敗，密碼錯誤")
        return user.username
    except Exception as e:
        raise Exception("{}".format(e))


def GetExpenses(acc, year_month):
    date_from, date_to = get_month_range(year_month)
    result = (
        Expenses.objects.select_related("category")
        .values("category__c_name", "e_date", "e_desc", "e_type", "e_amount", "e_id")
        .filter(username=acc, e_date__range=[date_from, date_to])
    )
    for item in result:
        # 將 e_amount 格式化為帶千分逗點的字符串
        item["e_amount"] = format(int(item["e_amount"]), ",")

    return list(result)


def GetEditExpense(acc, e_id):
    result = (
        Expenses.objects.values(
            "category", "e_date", "e_desc", "e_type", "e_amount", "e_id"
        ).filter(username=acc, e_id=e_id)
    ).first()
    return result


def GetSumExpenses(acc, year_month):
    date_from, date_to = get_month_range(year_month)
    grouped_expenses = (
        Expenses.objects.select_related("category")
        .values("category__c_name", "e_type")  # 用 ForeignKey 查詢該表格資料
        .annotate(total_spent=Sum("e_amount"))
        .filter(username=acc, e_date__range=[date_from, date_to])
    )

    for item in grouped_expenses:
        # 將 total_spent 格式化為帶千分逗點的字符串
        item["total_spent"] = format(int(item["total_spent"]), ",")
    return list(grouped_expenses)


def GetCategory(acc):
    category = Category.objects.values("c_id", "c_type", "c_name").filter(username=acc)
    return list(category)


def SaveExpense(model):
    try:
        with transaction.atomic():
            if model["e_id"] == "insert":
                expense = Expenses(
                    u_username=CustomUser.objects.get(username=model["current_user"]),
                    category=Category.objects.get(c_id=model["category"]),
                    e_date=model["date"],
                    e_type=model["type"],
                    e_amount=model["amount"],
                    e_desc=model["desc"],
                )
            else:
                expense = Expenses.objects.get(e_id=model["e_id"])
                expense.category = Category.objects.get(c_id=model["category"])
                expense.e_date = model["date"]
                expense.e_type = model["type"]
                expense.e_amount = model["amount"]
                expense.e_desc = model["desc"]
            # Save the user to the database
            expense.save()
    except Exception as e:
        raise Exception("{}".format(e))


def DeleteExpense(id, acc):
    try:
        with transaction.atomic():
            expense = Expenses.objects.get(e_id=id, u_username=acc)
            expense.delete()
    except Exception as e:
        raise Exception("{}".format(e))
