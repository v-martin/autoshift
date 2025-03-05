from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class CreateUserRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'uuid',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'avatar',
            'password',
        )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])

        return super().create(validated_data)


class UpdateUserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'avatar',
        )
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'phone_number': {'required': False},
            'avatar': {'required': False},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'uuid',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'avatar',
        )
