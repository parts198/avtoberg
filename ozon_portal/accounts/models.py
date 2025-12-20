from django.db import models
from django.contrib.auth.models import User

class BootstrapState(models.Model):
    executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"bootstrap_done={self.executed}"
