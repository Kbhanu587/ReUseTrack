from django.conf import settings
from django.db import models
from accounts.models import Business
from containers.models import Container


class Issue(models.Model):
    class Kind(models.TextChoices):
        LOST = 'LOST', 'Lost'
        DAMAGED = 'DAMAGED', 'Damaged'

    class Resolution(models.TextChoices):
        REPAIRED = 'REPAIRED', 'Repaired'
        FOUND = 'FOUND', 'Found'
        WRITTEN_OFF = 'WRITTEN_OFF', 'Written off'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='issues')
    container = models.ForeignKey(Container, on_delete=models.PROTECT, related_name='issues')
    assignment = models.ForeignKey(
        'assignments.Assignment', on_delete=models.PROTECT,
        null=True, blank=True, related_name='issues',
    )
    kind = models.CharField(max_length=10, choices=Kind.choices)
    description = models.TextField()
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reported_issues',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolution = models.CharField(max_length=15, choices=Resolution.choices, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-id']

    @property
    def is_open(self):
        return self.resolution == ''

    def __str__(self):
        return f"{self.container.code}: {self.get_kind_display()}"