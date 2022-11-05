from django.db import models
from app.models.week import Week


class Island(models.Model):
    def __str__(self) -> str:
        return self.title

    island_id = models.BigAutoField(primary_key=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    descript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
