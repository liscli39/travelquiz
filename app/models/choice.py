from django.db import models
from app.models.question import Question


class Choice(models.Model):
    def __str__(self):
        return str(self.choice_text)

    choice_id = models.BigAutoField(primary_key=True)
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
