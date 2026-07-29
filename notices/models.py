from django.db import models
from django.conf import settings
from core.models import BaseModel


class Notice(BaseModel):
    title = models.CharField(max_length=150)

    description = models.TextField()

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notices"
    )

    def __str__(self):
        return self.title
