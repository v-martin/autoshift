import uuid
from django.db import models
from django.conf import settings


class Warehouse(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    name = models.CharField(
        max_length=255,
    )
    address = models.TextField()
    capacity = models.PositiveIntegerField(
        help_text="Maximum number of workers allowed in the warehouse",
    )
    min_workers = models.PositiveIntegerField(
        help_text="Minimum number of workers required in the warehouse",
        default=0,
    )
    min_basic_workers = models.PositiveIntegerField(
        help_text="Minimum number of basic workers required in the warehouse",
        default=0,
    )
    min_drivers = models.PositiveIntegerField(
        help_text="Minimum number of cargo drivers required in the warehouse",
        default=0,
    )
    min_engineers = models.PositiveIntegerField(
        help_text="Minimum number of engineers required in the warehouse",
        default=0,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name 