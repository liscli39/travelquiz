from django.db import models
from app.models.choice import Choice
from app.models.user import User


class Answer(models.Model):
    answer_id = models.BigAutoField(primary_key=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.IntegerField(null=True, blank=True)
