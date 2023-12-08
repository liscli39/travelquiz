from django.db import models

class Chart(models.Model):
    char_id = models.BigAutoField(primary_key=True)
    date = models.DateField(null=True)
    user_count = models.IntegerField(default=0)
    anwser_count = models.IntegerField(default=0)
    anwser_correct = models.IntegerField(default=0)
