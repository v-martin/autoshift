import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission, UserManager
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    WORKER = 'worker'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (WORKER, 'Worker'),
        (ADMIN, 'Admin'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=WORKER,
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    username = models.CharField(
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    avatar = models.ImageField(
        upload_to='user_avatars',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS,
            ),
        ],
    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
    )
    is_admin_requested = models.BooleanField(
        default=False,
        help_text="Designates whether the user has requested an admin role.",
    )
    is_staff = models.BooleanField(
        default=False,
    )
    
    preferred_warehouses = models.ManyToManyField(
        'warehouses.Warehouse',
        through='WorkerWarehousePreference',
        related_name='preferred_by_workers',
        blank=True,
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class WorkerQualification(models.Model):
    BASIC_WORKER = 'basic_worker'
    CARGO_DRIVER = 'cargo_driver'
    ENGINEER = 'engineer'
    
    QUALIFICATION_CHOICES = [
        (BASIC_WORKER, 'Basic Worker'),
        (CARGO_DRIVER, 'Cargo Driver'),
        (ENGINEER, 'Engineer'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qualifications',
    )
    qualification_type = models.CharField(
        max_length=20,
        choices=QUALIFICATION_CHOICES,
    )
    level = models.PositiveSmallIntegerField(
        default=1,
        help_text="Skill level from 1 to 5",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'qualification_type']
        
    def __str__(self):
        return f"{self.user.username} - {self.get_qualification_type_display()} (Level {self.level})"


class WorkerWarehousePreference(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='warehouse_preferences',
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.CASCADE,
        related_name='worker_preferences',
    )
    priority = models.PositiveSmallIntegerField(
        default=1,
        help_text="Priority level (1 is highest)",
    )
    distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Distance in km from worker's location to the warehouse",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'warehouse']
        ordering = ['priority']
        
    def __str__(self):
        return f"{self.user.username} - {self.warehouse.name} (Priority: {self.priority})"
