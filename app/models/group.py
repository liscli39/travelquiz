from django.db import models
from app.utils.enum import Enum
from app.models.user import User
from app.utils.encryptor import PrimaryKeyEncryptor


class Group(models.Model):
    def __str__(self):
        return PrimaryKeyEncryptor().encrypt(self.group_id) + ' - ' + self.group_title

    group_id = models.BigAutoField(primary_key=True)
    group_title = models.CharField(max_length=255)
    status = models.SmallIntegerField(choices=Enum.GroupStatus, default=Enum.GROUP_STATUS_DEFAULT)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)