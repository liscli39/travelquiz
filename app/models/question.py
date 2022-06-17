from django.db import models
from app.models.week import Week

class Question(models.Model):
    def __str__(self):
        return (self.question_text[:60] + '..') if len(self.question_text) > 60 else self.question_text

    question_id = models.BigAutoField(primary_key=True)
    question_text = models.TextField()
    week = models.ForeignKey(Week, on_delete=models.CASCADE, null=True)
