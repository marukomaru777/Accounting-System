from .models import CustomUser, Expenses, Category, UserConfirmString
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db import transaction
from django.db.models import Q
from django.conf import settings
import calendar
import pytz


def IsAccExists(account):
    return CustomUser.objects.filter(Q(account=account) & Q(is_active=True)).exists()


def get_month_range(date_str):
    date = datetime.strptime(date_str, "%Y-%m")
    year = date.year
    month = date.month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    return start_date, end_date


def make_confirm_string(user):
    now = datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S")
    code = hash(user.account + now)
    UserConfirmString.objects.create(
        code=code,
        u_account_id=user.account,
    )
    return code


def Register(model):
    try:
        if not IsAccExists(model["account"]):
            with transaction.atomic():
                new_user = CustomUser(
                    account=model["account"],
                    password=make_password(model["password"]),
                    email=model["account"],
                    is_active=False,
                )
                # Save the user to the database
                new_user.save()

                code = make_confirm_string(new_user)
                SendRegisterMail(new_user.email, code)
        else:
            raise Exception("帳號已經存在 請重新登入")
    except Exception as e:
        raise Exception("{}".format(e))


def SendRegisterMail(email, code):
    try:
        subject = "I Need Money 註冊確認信"
        text_content = """
                        感謝註冊 I Need Money，祝您早日財富自由，不要屈服於資本主義！你我一起加油吧！
                        如果您看到這則訊息，代表您的email不提供HTML功能，請聯絡管理員，謝謝！
                        """
        html_content = """
        <p>感謝註冊 I Need Money，祝您早日財富自由，不要屈服於資本主義！你我一起加油吧！</p>
                        <p><a href="http://{}/accounting/confirm/?code={}" target=blank>點此完成註冊</a></p>
                        <p>此連結有效期限為{}天</p>
                        """.format(
            settings.WEB_URL, code, settings.CONFIRM_DAYS
        )

        msg = EmailMultiAlternatives(
            subject, text_content, settings.EMAIL_HOST_USER, [email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        raise Exception("{}".format(e))


def ConfirmRegistration(code):
    try:
        user_confirm = UserConfirmString.objects.filter(Q(code=code)).first()
        if not user_confirm:
            return "註冊連結不存在"
        with transaction.atomic():
            create_time = user_confirm.create_time
            now = datetime.now(pytz.timezone(settings.TIME_ZONE))
            if now > create_time + timedelta(days=settings.CONFIRM_DAYS):
                user_confirm.u_account.delete()
                message = "郵件已過期，請重新註冊"
            else:
                user_confirm.u_account.is_active = True
                user_confirm.u_account.save()

                expense_list = ["飲食", "繳費", "日常", "購物", "娛樂", "其他"]
                income_list = ["薪水", "獎金", "兼職", "投資", "零用錢", "其他"]
                for i in income_list:
                    Category.objects.create(
                        u_account_id=user_confirm.u_account.account,
                        c_type="+",
                        c_name=i,
                    )
                for i in expense_list:
                    Category.objects.create(
                        u_account_id=user_confirm.u_account.account,
                        c_type="-",
                        c_name=i,
                    )

                user_confirm.delete()
                message = "註冊完成，請登入"
    except Exception as e:
        raise Exception("{}".format(e))
    return message


def Login(model):
    try:
        user = CustomUser.objects.filter(
            Q(account=model["account"]) & Q(is_active=True)
        ).first()
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
        .values("category__c_name", "e_date", "e_desc", "e_type", "e_amount", "e_id")
        .filter(u_account_id=acc, e_date__range=[date_from, date_to])
    )
    for item in result:
        # 將 e_amount 格式化為帶千分逗點的字符串
        item["e_amount"] = format(int(item["e_amount"]), ",")

    return list(result)


def GetEditExpense(acc, e_id):
    result = (
        Expenses.objects.values(
            "category", "e_date", "e_desc", "e_type", "e_amount", "e_id"
        ).filter(u_account_id=acc, e_id=e_id)
    ).first()
    return result


def GetSumExpenses(acc, year_month):
    date_from, date_to = get_month_range(year_month)
    grouped_expenses = (
        Expenses.objects.select_related("category")
        .values(
            "category__c_name", "e_type"
        )  # 通过外键关联的模型名加上字段名来访问相关字段
        .annotate(total_spent=Sum("e_amount"))
        .filter(u_account_id=acc, e_date__range=[date_from, date_to])
    )

    for item in grouped_expenses:
        # 將 total_spent 格式化為帶千分逗點的字符串
        item["total_spent"] = format(int(item["total_spent"]), ",")
    return list(grouped_expenses)


def GetCategory(acc):
    category = Category.objects.values("c_id", "c_type", "c_name").filter(
        u_account_id=acc
    )
    return list(category)


def SaveExpense(model):
    try:
        with transaction.atomic():
            if model["e_id"] == "insert":
                expense = Expenses(
                    u_account=CustomUser.objects.get(account=model["current_user"]),
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
            expense = Expenses.objects.get(e_id=id, u_account=acc)
            expense.delete()
    except Exception as e:
        raise Exception("{}".format(e))
