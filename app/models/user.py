from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
import time


class UserManager(BaseUserManager):
    def _create_user(self, phone, password, **extra_fields):
        # if there is a deleted user that already exists
        phone_exist = User.objects.filter(phone=phone, deleted=True).first()
        if phone_exist is not None:
            deleted_phone = 'del_' + int(time.time()).__str__() + '_' + phone
            phone_exist.__dict__.update(phone=deleted_phone, **extra_fields)
            phone_exist.save()

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    def __str__(self):
        return self.name

    user_id = models.BigAutoField(primary_key=True)
    phone = models.CharField(_('phone'), max_length=12, unique=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    office = models.CharField(max_length=200, null=True, blank=True)
    token = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    password_reset = models.BooleanField(default=False)

    username = None
    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    @property
    def is_valid(self):
        return (self is not None
                and not self.deleted
                and not self.password_reset
                and self.is_active)
