import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class CargoLoad(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='cargo_loads',
    )
    date = models.DateField()
    
    total_weight = models.PositiveIntegerField(
        help_text="Total cargo weight in kg",
        validators=[MinValueValidator(0)],
        default=0,
    )
    
    estimated_basic_workers = models.PositiveIntegerField(
        help_text="Estimated number of basic workers needed for this load",
        default=0,
    )
    estimated_drivers = models.PositiveIntegerField(
        help_text="Estimated number of drivers needed for this load",
        default=0,
    )
    estimated_engineers = models.PositiveIntegerField(
        help_text="Estimated number of engineers needed for this load",
        default=0,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['warehouse', 'date']
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.warehouse.name} - {self.date}"
    
    def calculate_staff_requirements(self):
        self.estimated_basic_workers = max(
            self.warehouse.min_basic_workers,
            (self.total_weight // 1000) + (1 if self.total_weight % 1000 > 0 else 0)
        )
        
        self.estimated_drivers = max(
            self.warehouse.min_drivers,
            (self.total_weight // 5000) + (1 if self.total_weight % 5000 > 0 else 0)
        )
        
        self.estimated_engineers = max(
            self.warehouse.min_engineers,
            (self.total_weight // 10000) + (1 if self.total_weight % 10000 > 0 else 0)
        )
        
        return {
            'basic_workers': self.estimated_basic_workers,
            'drivers': self.estimated_drivers,
            'engineers': self.estimated_engineers,
        }
    
    def save(self, *args, **kwargs):
        self.calculate_staff_requirements()
        super().save(*args, **kwargs)


class CargoForecast(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='cargo_forecasts',
    )
    date = models.DateField()
    
    forecasted_weight = models.PositiveIntegerField(
        help_text="Forecasted total cargo weight in kg",
        validators=[MinValueValidator(0)],
        default=0,
    )
    
    forecasted_basic_workers = models.PositiveIntegerField(
        help_text="Forecasted number of basic workers needed",
        default=0,
    )
    forecasted_drivers = models.PositiveIntegerField(
        help_text="Forecasted number of drivers needed",
        default=0,
    )
    forecasted_engineers = models.PositiveIntegerField(
        help_text="Forecasted number of engineers needed",
        default=0,
    )
    
    confidence_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Confidence level of the forecast (0-100%)",
        validators=[MinValueValidator(0)],
        default=0,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['warehouse', 'date']
        ordering = ['date']
        
    def __str__(self):
        return f"{self.warehouse.name} - {self.date} (Forecast)"
