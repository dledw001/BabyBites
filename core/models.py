import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Baby(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="babies",
        db_index=True,
    )

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('owner', 'name')]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
