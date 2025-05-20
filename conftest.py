"""
This file contains pytest fixtures and configuration for the test suite.
"""
import pytest
from datetime import time
from rest_framework.test import APIClient

@pytest.fixture(scope='session')
def django_db_setup():
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    from user.models import User
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="password123",
        is_staff=True,
        role='admin'
    )

@pytest.fixture
def worker_user(db):
    from user.models import User
    return User.objects.create_user(
        username="worker",
        email="worker@example.com",
        password="password123",
        role='worker'
    )

@pytest.fixture
def warehouse(db):
    from warehouses.models import Warehouse
    return Warehouse.objects.create(
        name="Test Warehouse",
        address="123 Test St",
        capacity=50,
        min_workers=3,
        min_basic_workers=1,
        min_drivers=1,
        min_engineers=1
    )

@pytest.fixture
def worker_qualification(db, worker_user):
    from user.models import WorkerQualification
    return WorkerQualification.objects.create(
        user=worker_user,
        qualification_type=WorkerQualification.BASIC_WORKER,
        level=3
    )

@pytest.fixture
def worker_preference(db, worker_user, warehouse):
    from user.models import WorkerWarehousePreference
    return WorkerWarehousePreference.objects.create(
        user=worker_user,
        warehouse=warehouse,
        priority=1,
        distance=5.5
    )

@pytest.fixture
def shift(db, worker_user, warehouse):
    from shifts.models import Shift
    return Shift.objects.create(
        day_of_week=Shift.MONDAY,
        start_time=time(9, 0),
        end_time=time(17, 0),
        user=worker_user,
        warehouse=warehouse
    )

@pytest.fixture
def cargo_load(db, warehouse):
    from cargo.models import CargoLoad
    return CargoLoad.objects.create(
        warehouse=warehouse,
        date="2023-01-01",
        total_weight=5000
    ) 