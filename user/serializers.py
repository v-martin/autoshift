from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


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
            'id',
            'uuid',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'avatar',
        )


class SignUpRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2',
            'role',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': '''Password fields didn't match.'''})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.WORKER,
            is_admin_requested=(validated_data['role'] == User.ADMIN),
        )

        return user


class RefreshTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    user = UserResponseSerializer(read_only=True)
    token = serializers.SerializerMethodField()

    @extend_schema_field(RefreshTokenResponseSerializer())
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj['user'])

        return RefreshTokenResponseSerializer({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }).data


class SignInRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminRoleApproveRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=['approve', 'reject'],
        write_only=True,
    )
