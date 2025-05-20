import pytest
import json
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from warehouses.models import Warehouse
from shifts.models import Shift
from user.models import User

# Mark all tests to use the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="password123",
        is_staff=True,
        role='admin'
    )


@pytest.fixture
def worker_user():
    return User.objects.create_user(
        username="worker",
        email="worker@example.com",
        password="password123",
        role='worker'
    )


@pytest.fixture
def warehouse():
    return Warehouse.objects.create(
        name="Test Warehouse",
        address="123 Test St",
        capacity=50
    )


@pytest.fixture
def shift(worker_user, warehouse):
    return Shift.objects.create(
        day_of_week=Shift.MONDAY,
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=8),
        user=worker_user,
        warehouse=warehouse
    )


class TestShiftAPI:
    def test_list_shifts(self, db):
        client = APIClient()
        warehouse = Warehouse.objects.create(
            name="Warehouse A",
            address="123 Test St",
            capacity=50
        )
        
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=8)
        
        Shift.objects.create(
            warehouse=warehouse,
            start_time=start_time,
            end_time=end_time,
            required_workers=5
        )
        
        url = reverse('shifts-list')
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        
    def test_retrieve_shift(self, api_client, admin_user, shift):
        api_client.force_authenticate(user=admin_user)
        url = reverse('shift-detail', args=[shift.uuid])
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['day_of_week'] == Shift.MONDAY
        assert response.data['start_time'] == shift.start_time.isoformat()
        assert response.data['end_time'] == shift.end_time.isoformat()
        
    def test_create_shift(self, db):
        client = APIClient()
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        client.force_authenticate(user=admin_user)
        
        warehouse = Warehouse.objects.create(
            name="Warehouse B",
            address="456 Test Ave",
            capacity=30
        )
        
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=4)
        
        data = {
            'warehouse': warehouse.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'required_workers': 3
        }
        
        url = reverse('shifts-list')
        response = client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert Shift.objects.count() == 1
        
    def test_update_shift(self, api_client, admin_user, shift, worker_user, warehouse):
        api_client.force_authenticate(user=admin_user)
        url = reverse('shift-detail', args=[shift.uuid])
        data = {
            'day_of_week': Shift.WEDNESDAY,
            'start_time': shift.start_time.isoformat(),
            'end_time': shift.end_time.isoformat(),
            'user': worker_user.id,
            'warehouse': warehouse.id
        }
        response = api_client.put(url, data)
        assert response.status_code == 200
        
        # Refresh from database
        shift.refresh_from_db()
        assert shift.day_of_week == Shift.WEDNESDAY
        assert shift.start_time == timezone.now()
        assert shift.end_time == timezone.now() + timedelta(hours=8)
        
    def test_partial_update_shift(self, api_client, admin_user, shift):
        api_client.force_authenticate(user=admin_user)
        url = reverse('shift-detail', args=[shift.uuid])
        data = {
            'day_of_week': Shift.FRIDAY
        }
        response = api_client.patch(url, data)
        assert response.status_code == 200
        
        # Refresh from database
        shift.refresh_from_db()
        assert shift.day_of_week == Shift.FRIDAY
        # Original value should remain unchanged
        assert shift.start_time == timezone.now()
        
    def test_delete_shift(self, api_client, admin_user, shift):
        api_client.force_authenticate(user=admin_user)
        url = reverse('shift-detail', args=[shift.uuid])
        response = api_client.delete(url)
        assert response.status_code == 204
        assert Shift.objects.count() == 0
        
    def test_worker_access_own_shifts(self, api_client, worker_user, shift):
        # Have the worker access their own shift
        api_client.force_authenticate(user=worker_user)
        url = reverse('shift-detail', args=[shift.uuid])
        response = api_client.get(url)
        assert response.status_code == 200
        
    def test_worker_shifts_filter(self, api_client, worker_user, warehouse, shift):
        # Create another user with a shift
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="password123"
        )
        Shift.objects.create(
            day_of_week=Shift.THURSDAY,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=8),
            user=other_user,
            warehouse=warehouse
        )
        
        # Test that the worker only sees their own shifts
        api_client.force_authenticate(user=worker_user)
        url = reverse('shift-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1  # Only their own shift

    def test_get_shift_detail(self, db):
        client = APIClient()
        warehouse = Warehouse.objects.create(
            name="Warehouse C",
            address="789 Test Blvd",
            capacity=40
        )
        
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=6)
        
        shift = Shift.objects.create(
            warehouse=warehouse,
            start_time=start_time,
            end_time=end_time,
            required_workers=10
        )
        
        url = reverse('shifts-detail', args=[shift.id])
        response = client.get(url)
        
        assert response.status_code == 200
        assert response.data['id'] == shift.id
        assert response.data['warehouse'] == warehouse.id 