from django.db import models
from datetime import datetime
from users.models import CustomUser
from django.utils import timezone

# Create your models here.


class Category(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    username = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_category",
        to_field="username",
    )
    c_type = models.CharField(max_length=2)
    c_name = models.CharField(max_length=50)
    c_icon = models.CharField(max_length=200)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tb_category"  # table name


class Expenses(models.Model):
    e_id = models.BigAutoField(primary_key=True)
    username = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_expenses",
        to_field="username",
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
    e_desc = models.CharField(max_length=500, null=True)
    create_time = models.DateTimeField(default=timezone.now)

    # 定義表的元data：描述其他數據的元素
    class Meta:
        db_table = "tb_expenses"  # table name


class ExpenseResult:
    def __init__(self, result=False, e_type="-", e_amount=0, e_desc="", c_id=0):
        self.result = result
        self.type = e_type
        self.e_amount = e_amount
        self.e_desc = e_desc
        self.c_id = c_id
        self.e_date = datetime.now().strftime("%Y-%m-%d")
