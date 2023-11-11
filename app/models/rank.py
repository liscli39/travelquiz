from django.db import models
from app.models.week import Week
from app.models.user import User


class Rank(models.Model):
    rank_id = models.BigAutoField(primary_key=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    selected = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    corrects = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    predict = models.IntegerField(default=0)
