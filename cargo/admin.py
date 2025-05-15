from django.contrib import admin
from .models import CargoLoad, CargoForecast


@admin.register(CargoLoad)
class CargoLoadAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'date', 'total_weight', 'estimated_basic_workers',
                    'estimated_drivers', 'estimated_engineers')
    list_filter = ('warehouse', 'date')
    search_fields = ('warehouse__name',)
    date_hierarchy = 'date'


@admin.register(CargoForecast)
class CargoForecastAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'date', 'forecasted_weight', 
                    'forecasted_basic_workers', 'forecasted_drivers', 
                    'forecasted_engineers', 'confidence_level')
    list_filter = ('warehouse', 'date')
    search_fields = ('warehouse__name',)
    date_hierarchy = 'date'
