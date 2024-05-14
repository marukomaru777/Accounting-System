from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
# 建立用戶模型
class CustomUser(AbstractUser):
    account = models.CharField(max_length=100, primary_key=True, unique=True)
    password = models.CharField(max_length=100)
    line_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(default=False)

    # 認證欄位
    USERNAME_FIELD = "account"

    # superuser必須輸入的欄位
    REQUIRED_FIELDS = ["username", "email"]

    class Meta:
        db_table = "tb_user"  # table name
        verbose_name = "使用者管理"  # admin 後台顯示
        verbose_name_plural = verbose_name  # admin 後台顯示

    def __str__(self):
        return self.account


class UserConfirmString(models.Model):
    code = models.CharField(max_length=2000)
    u_account = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        to_field="account",
    )
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        db_table = "tb_user_confirm_string"
        ordering = ["-create_time"]
