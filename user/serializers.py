from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import WorkerQualification, WorkerWarehousePreference


User = get_user_model()


class WorkerQualificationSerializer(serializers.ModelSerializer):
    qualification_type_display = serializers.CharField(source='get_qualification_type_display', read_only=True)
    
    class Meta:
        model = WorkerQualification
        fields = ('id', 'qualification_type', 'qualification_type_display', 'level', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_qualification_type(self, value):
        if value not in dict(WorkerQualification.QUALIFICATION_CHOICES):
            raise serializers.ValidationError(f"Invalid qualification type. Choose from: {', '.join(dict(WorkerQualification.QUALIFICATION_CHOICES).keys())}")
        return value
    
    def validate_level(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Level must be between 1 and 5")
        return value
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            qualification_type = attrs.get('qualification_type')
            
            if self.instance is None and WorkerQualification.objects.filter(
                user=user, 
                qualification_type=qualification_type
            ).exists():
                raise serializers.ValidationError({
                    "qualification_type": f"You already have a {dict(WorkerQualification.QUALIFICATION_CHOICES).get(qualification_type)} qualification."
                })
        
        return attrs


class WorkerQualificationCreateSerializer(WorkerQualificationSerializer):
    class Meta(WorkerQualificationSerializer.Meta):
        fields = ('qualification_type', 'level')


class WorkerWarehousePreferenceSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = WorkerWarehousePreference
        fields = ('id', 'warehouse', 'warehouse_name', 'priority', 'distance', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_priority(self, value):
        if value < 1:
            raise serializers.ValidationError("Priority must be at least 1 (highest priority)")
        return value
    
    def validate_distance(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Distance cannot be negative")
        return value
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            warehouse = attrs.get('warehouse')
            
            if self.instance is None and warehouse and WorkerWarehousePreference.objects.filter(
                user=user, 
                warehouse=warehouse
            ).exists():
                raise serializers.ValidationError({
                    "warehouse": f"You already have a preference for warehouse {warehouse.name}."
                })
        
        return attrs


class WorkerWarehousePreferenceCreateSerializer(WorkerWarehousePreferenceSerializer):
    class Meta(WorkerWarehousePreferenceSerializer.Meta):
        fields = ('warehouse', 'priority', 'distance')


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
    qualifications = WorkerQualificationSerializer(many=True, read_only=True)
    warehouse_preferences = WorkerWarehousePreferenceSerializer(many=True, read_only=True)
    
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
            'qualifications',
            'warehouse_preferences',
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
    avatar = serializers.ImageField(required=False)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(required=False, max_length=150)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2',
            'role',
            'avatar',
            'first_name',
            'last_name',
            'phone_number',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': '''Password fields didn't match.'''})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role', User.WORKER)
        
        user = User.objects.create_user(
            username=validated_data.pop('username'),
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            role=User.WORKER,
            is_admin_requested=(role == User.ADMIN),
            **validated_data
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
