import uuid
from django.db import models
from django.conf import settings


class Shift(models.Model):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'
    
    DAY_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    ]
    
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=DAY_CHOICES,
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shifts',
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='shifts',
    )
    is_optimized = models.BooleanField(
        default=False,
        help_text="Флаг, указывающий, что смена была создана автоматически через оптимизацию"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['user', 'day_of_week', 'start_time'] 