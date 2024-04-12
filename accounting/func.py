from bot.models import User, Expenses, Category, ExpenseResult
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password


def GetExpenses():
    with connection.cursor() as cursor:
        sql = """
        SELECT *
        FROM expenses;
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        return row


from django.db import transaction
from django.db.models import Q


def IsAccExists(account):
    return User.objects.filter(Q(user_id=account) | Q(account=account)).exists()


def Register(model):
    try:
        if not IsAccExists(model["account"]):
            with transaction.atomic():
                # new_user = User(
                #     user_id=model["account"],
                #     account=model["account"],
                #     password=make_password(model["password"]),
                # )
                # # Save the user to the database
                # new_user.save()
                # expense_list = ["飲食", "繳費", "日常", "購物", "娛樂", "其他"]
                # income_list = ["薪水", "獎金", "兼職", "投資", "零用錢", "其他"]
                # for i in income_list:
                #     Category.objects.create(
                #         user_id=model["account"], c_type="+", c_name=i
                #     )
                # for i in expense_list:
                #     Category.objects.create(
                #         user_id=model["account"], c_type="-", c_name=i
                #     )
                return True
        else:
            Exception("帳號已經存在 請重新登入")
    except Exception as e:
        Exception("Unexpected error: {}".format(e))


def Login(model):
    try:
        return User.objects.filter(account=model["account"]).first()
    except Exception as e:
        Exception("Unexpected error: {}".format(e))
