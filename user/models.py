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

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
