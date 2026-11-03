from django.conf import settings
from django.db import models
from accounts.models import Business


class Notification(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True)
    key = models.CharField(max_length=100, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        unique_together = ('user', 'key')

    def __str__(self):
        return f"{self.user} - {self.message[:40]}"