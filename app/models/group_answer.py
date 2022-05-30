from django.db import models
from app.models.choice import Choice
from app.models.user import User
from app.models.question import Question
from app.models.group import Group


class GroupAnswer(models.Model):
    group_answer_id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
