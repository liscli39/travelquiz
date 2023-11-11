from django.db import models

class Week(models.Model):
    def __str__(self) -> str:
        return self.name

    week_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rank_updated_at = models.DateTimeField(null=True)
    show_rank = models.BooleanField(null=True, blank=True, unique=True)
    limit_time = models.IntegerField(default=120000)
    limit_question = models.IntegerField(default=20)
