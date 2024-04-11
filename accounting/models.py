from django.db import models
from datetime import datetime

# Create your models here.


# Create your models here.
# 建立用戶模型
class User(models.Model):
    user_id = models.CharField(max_length=100)
    account = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    # 定義表的元data：描述其他數據的元素
    class Meta:
        db_table = "user"  # table name


class Category(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    c_type = models.CharField(max_length=2)
    c_name = models.CharField(max_length=50)
    c_icon = models.CharField(max_length=200)

    class Meta:
        db_table = "category"  # table name


class Expenses(models.Model):
    e_id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    c_id = models.IntegerField()
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
