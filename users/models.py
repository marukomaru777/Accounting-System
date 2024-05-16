# Create your models here.
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, username, password, is_staff, is_active, is_superuser, **extra_fields
    ):
        """
        Creates and saves a User with the given username and password.

        New user: username = email.
        """
        now = timezone.now()
        if not username:
            raise ValueError("The given email must be set")
        username = self.normalize_email(username)
        user = self.model(
            username=username,
            email=username,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(
            username, password, False, False, False, **extra_fields
        )

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True, True, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    username and password are required. Other fields are optional.
    """

    username = models.EmailField(max_length=254, primary_key=True, unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)

    # Admin
    is_staff = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=False,
    )

    date_joined = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "tb_user"  # table name
        verbose_name = "使用者管理"  # admin 後台顯示
        verbose_name_plural = verbose_name

    def email_user(self, subject, message, from_email=None, html_message=None):
        """
        Sends an email to this User.
        """
        send_mail(
            subject,
            message,
            from_email,
            [self.email],
            fail_silently=True,
            html_message=html_message,
        )


class UserConfirmString(models.Model):
    code = models.CharField(max_length=2000)
    username = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        to_field="username",
    )
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        db_table = "tb_user_confirm_string"
        ordering = ["-create_time"]
