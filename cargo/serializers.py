from rest_framework import serializers
from .models import CargoLoad, CargoForecast


class CargoLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoLoad
        fields = [
            'uuid', 'warehouse', 'date', 'total_weight',
            'estimated_basic_workers', 'estimated_drivers', 'estimated_engineers',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'uuid', 'estimated_basic_workers', 'estimated_drivers', 'estimated_engineers',
            'created_at', 'updated_at'
        ]


class CargoForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoForecast
        fields = [
            'uuid', 'warehouse', 'date', 'forecasted_weight',
            'forecasted_basic_workers', 'forecasted_drivers',
            'forecasted_engineers', 'confidence_level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at'] 