from django.db import models
from datetime import datetime


# Create your models here.
from accounting.models import Category, Expenses
from users.models import CustomUser

class ExpenseResult:
    def __init__(self, result=False, e_type="-", e_amount=0, e_desc="", c_id=0):
        self.result = result
        self.type = e_type
        self.e_amount = e_amount
        self.e_desc = e_desc
        self.c_id = c_id
        self.e_date = datetime.now().strftime("%Y-%m-%d")