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
            'is_active',
        )
        extra_kwargs = {
            'name': {'required': False},
            'address': {'required': False},
            'capacity': {'required': False},
            'min_workers': {'required': False},
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
            'is_active',
            'created_at',
            'updated_at',
        ) 