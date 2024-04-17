from django.db import models
from datetime import datetime

# Create your models here.


# Create your models here.
# 建立用戶模型
class CustomUser(models.Model):
    account = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)
    line_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=200, null=True)

    # 定義表的元data：描述其他數據的元素
    class Meta:
        db_table = "user"  # table name


class Category(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    u_account = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_category",
        to_field="account",
    )
    c_type = models.CharField(max_length=2)
    c_name = models.CharField(max_length=50)
    c_icon = models.CharField(max_length=200)

    class Meta:
        db_table = "category"  # table name


class Expenses(models.Model):
    e_id = models.BigAutoField(primary_key=True)
    u_account = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_expenses",
        to_field="account",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_expenses",
        to_field="c_id",
    )
    e_date = models.DateField()
    e_type = models.CharField(max_length=2)
    e_amount = models.FloatField()
    e_desc = models.CharField(max_length=500)

    # 定義表的元data：描述其他數據的元素
    class Meta:
        db_table = "expenses"  # table name


class ExpenseResult:
    def __init__(self, result=False, e_type="-", e_amount=0, e_desc="", c_id=0):
        self.result = result
        self.type = e_type
        self.e_amount = e_amount
        self.e_desc = e_desc
        self.c_id = c_id
        self.e_date = datetime.now().strftime("%Y-%m-%d")
