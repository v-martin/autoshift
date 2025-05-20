import pytest
from django.utils import timezone
from datetime import timedelta

from user.models import User
from warehouses.models import Warehouse
from shifts.models import Shift

# Mark all tests to use the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )


@pytest.fixture
def warehouse():
    return Warehouse.objects.create(
        name="Test Warehouse",
        address="123 Test St",
        capacity=50
    )


class TestShiftModel:
    def test_shift_creation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift.objects.create(
            warehouse=warehouse,
            start_time=start_time,
            end_time=end_time,
            required_workers=5
        )
        
        assert shift.warehouse == warehouse
        assert shift.start_time == start_time
        assert shift.end_time == end_time
        assert shift.required_workers == 5
        assert shift.assigned_workers == 0
        
    def test_shift_string_representation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift.objects.create(
            warehouse=warehouse,
            start_time=start_time,
            end_time=end_time,
            required_workers=5
        )
        
        expected_string = f"{warehouse.name} - {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}"
        assert str(shift) == expected_string 