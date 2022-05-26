from django.db import models
from app.models import User, Group
from app.utils.enum import Enum

class GroupUser(models.Model):
    def __str__(self):
        return str(self.group) + ' - ' + str(self.user)

    group_user_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=Enum.GroupUserStatus, default=Enum.USER_GROUP_STATUS_DEFAULT)

    class Meta:
        unique_together = ('user', 'group')
