from django.db import models
from app.models.choice import Choice
from app.models.user import User
from app.models.question import Question


class Answer(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['answer_at']),
        ]

    answer_id = models.BigAutoField(primary_key=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.IntegerField(null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    turn = models.CharField(null=True, blank=True, max_length=255)
    answer_at = models.DateTimeField(auto_now_add=True, null=True)
