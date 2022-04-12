from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
import time


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        # if there is a deleted user that already exists
        email_exist = User.objects.filter(email=email, deleted=True).first()
        if email_exist is not None:
            deleted_email = 'del_' + int(time.time()).__str__() + '_' + email
            email_exist.__dict__.update(email=deleted_email, **extra_fields)
            email_exist.save()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    def __str__(self):
        return self.email

    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(_('email'), unique=True)
    is_active = models.BooleanField(default=False, verbose_name='有効なユーザー')
    deleted = models.BooleanField(default=False, verbose_name='削除フラグ')
    password_reset = models.BooleanField(default=False, verbose_name='パスワードリセットフラグ')
    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_valid(self):
        return (self is not None
                and not self.deleted
                and not self.password_reset
                and self.is_active)
