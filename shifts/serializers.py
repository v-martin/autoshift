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
            'created_at',
            'updated_at',
        ) 