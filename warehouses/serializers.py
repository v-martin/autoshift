from rest_framework import serializers
from warehouses.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'id',
            'uuid',
            'name',
            'address',
            'capacity',
            'min_workers',
            'min_basic_workers',
            'min_drivers',
            'min_engineers',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'uuid',
            'created_at',
            'updated_at',
        )


class WarehouseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'name',
            'address',
            'capacity',
            'min_workers',
            'min_basic_workers',
            'min_drivers',
            'min_engineers',
            'is_active',
        )


class WarehouseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'name',
            'address',
            'capacity',
            'min_workers',
            'min_basic_workers',
            'min_drivers',
            'min_engineers',
            'is_active',
        )
        extra_kwargs = {
            'name': {'required': False},
            'address': {'required': False},
            'capacity': {'required': False},
            'min_workers': {'required': False},
            'min_basic_workers': {'required': False},
            'min_drivers': {'required': False},
            'min_engineers': {'required': False},
            'is_active': {'required': False},
        }


class WarehouseResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'id',
            'uuid',
            'name',
            'address',
            'capacity',
            'min_workers',
            'min_basic_workers',
            'min_drivers',
            'min_engineers',
            'is_active',
            'created_at',
            'updated_at',
        ) 