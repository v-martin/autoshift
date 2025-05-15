from rest_framework import serializers
from shifts.models import Shift
from user.models import User


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'uuid',
            'day_of_week',
            'start_time',
            'end_time',
            'user',
            'warehouse',
            'is_optimized',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'uuid',
            'created_at',
            'updated_at',
        )


class ShiftCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'day_of_week',
            'start_time',
            'end_time',
            'user',
            'warehouse',
            'is_optimized',
        )
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        if user.role != User.ADMIN and attrs.get('user') and attrs['user'] != user:
            raise serializers.ValidationError({'user': 'You can only create shifts for yourself.'})
        
        if 'user' not in attrs:
            attrs['user'] = user
            
        return attrs


class ShiftUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'day_of_week',
            'start_time',
            'end_time',
            'warehouse',
            'is_optimized',
        )


class ShiftResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'uuid',
            'day_of_week',
            'start_time',
            'end_time',
            'user',
            'warehouse',
            'is_optimized',
            'created_at',
            'updated_at',
        )


class ShiftOptimizationRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False)
    warehouse_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False
    )
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date', start_date)
        
        if start_date > end_date:
            raise serializers.ValidationError({'end_date': 'End date cannot be before start date'})
        
        delta = end_date - start_date
        if delta.days > 14:
            raise serializers.ValidationError({'date_range': 'Optimization period cannot exceed 14 days'})
        
        return attrs


class WarehouseStaffingSerializer(serializers.Serializer):
    warehouse_uuid = serializers.CharField()
    warehouse_name = serializers.CharField()
    day = serializers.CharField()
    required_basic_workers = serializers.IntegerField()
    scheduled_basic_workers = serializers.IntegerField()
    required_drivers = serializers.IntegerField()
    scheduled_drivers = serializers.IntegerField()
    required_engineers = serializers.IntegerField()
    scheduled_engineers = serializers.IntegerField()
    is_fully_staffed = serializers.BooleanField()


class OptimizedShiftSerializer(serializers.Serializer):
    worker_uuid = serializers.CharField()
    warehouse_uuid = serializers.CharField()
    day_of_week = serializers.CharField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()


class ShiftOptimizationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    shifts = OptimizedShiftSerializer(many=True)
    warehouse_staffing = WarehouseStaffingSerializer(many=True) 