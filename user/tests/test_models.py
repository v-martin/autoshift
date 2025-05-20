import pytest
from django.test import TestCase

from user.models import User, WorkerQualification, WorkerWarehousePreference
from warehouses.models import Warehouse

# Mark all tests to use the database
pytestmark = pytest.mark.django_db

class TestUserModel:
    def test_user_creation(self, db):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        
        assert isinstance(user, User)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == User.WORKER  # Default role
        assert user.is_staff == False
        assert user.is_admin_requested == False
        
    def test_create_admin_user(self, db):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        assert admin.role == User.ADMIN
        assert admin.is_staff == True
        assert admin.is_superuser == True


class TestWorkerQualificationModel:
    def test_qualification_creation(self, db):
        user = User.objects.create_user(
            username="worker",
            email="worker@example.com",
            password="password123"
        )
        
        qualification = WorkerQualification.objects.create(
            user=user,
            qualification_type=WorkerQualification.BASIC_WORKER,
            level=3
        )
        
        assert isinstance(qualification, WorkerQualification)
        assert qualification.user == user
        assert qualification.qualification_type == WorkerQualification.BASIC_WORKER
        assert qualification.level == 3
        assert str(qualification) == f"{user.username} - Basic Worker (Level 3)"


class TestWorkerWarehousePreferenceModel:
    def test_preference_creation(self, db):
        user = User.objects.create_user(
            username="worker",
            email="worker@example.com",
            password="password123"
        )
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        preference = WorkerWarehousePreference.objects.create(
            user=user,
            warehouse=warehouse,
            priority=1,
            distance=5.5
        )
        
        assert isinstance(preference, WorkerWarehousePreference)
        assert preference.user == user
        assert preference.warehouse == warehouse
        assert preference.priority == 1
        assert preference.distance == 5.5
        assert str(preference) == f"{user.username} - {warehouse.name} (Priority: 1)" 