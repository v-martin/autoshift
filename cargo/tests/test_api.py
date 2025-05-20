import pytest
import json
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User
from warehouses.models import Warehouse
from cargo.models import CargoLoad, CargoForecast

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
        is_staff=True
    )


@pytest.fixture
def warehouse():
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
def cargo_load(warehouse):
    return CargoLoad.objects.create(
        warehouse=warehouse,
        date=date.today(),
        total_weight=5000
    )


class TestCargoLoadAPI:
    def test_list_cargo_loads(self, db):
        client = APIClient()
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50,
            min_workers=3,
            min_basic_workers=1,
            min_drivers=1,
            min_engineers=1
        )
        
        CargoLoad.objects.create(
            warehouse=warehouse,
            date=date.today(),
            total_weight=5000
        )
        
        url = reverse('cargo-loads-list')
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        
    def test_retrieve_cargo_load(self, api_client, admin_user, cargo_load):
        api_client.force_authenticate(user=admin_user)
        url = reverse('cargoload-detail', args=[cargo_load.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_weight'] == 5000
        
    def test_create_cargo_load(self, db):
        client = APIClient()
        
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        client.force_authenticate(user=admin_user)
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        data = {
            'warehouse': warehouse.id,
            'date': date.today().isoformat(),
            'total_weight': 6000
        }
        
        url = reverse('cargo-loads-list')
        response = client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert CargoLoad.objects.count() == 1
        
    def test_get_cargo_load_detail(self, db):
        client = APIClient()
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        cargo_load = CargoLoad.objects.create(
            warehouse=warehouse,
            date=date.today(),
            total_weight=5000
        )
        
        url = reverse('cargo-loads-detail', args=[cargo_load.id])
        response = client.get(url)
        
        assert response.status_code == 200
        assert response.data['id'] == cargo_load.id
        assert response.data['warehouse'] == warehouse.id
        assert response.data['total_weight'] == 5000
        
    def test_for_warehouse_filter(self, api_client, admin_user, warehouse, cargo_load):
        api_client.force_authenticate(user=admin_user)
        url = reverse('cargoload-for-warehouse')
        response = api_client.get(url, {'warehouse_uuid': warehouse.uuid})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        
    def test_by_date_range(self, api_client, admin_user, warehouse, cargo_load):
        # Create a cargo load for tomorrow
        tomorrow = date.today().replace(day=date.today().day + 1)
        CargoLoad.objects.create(
            warehouse=warehouse,
            date=tomorrow,
            total_weight=2000
        )
        
        api_client.force_authenticate(user=admin_user)
        url = reverse('cargoload-by-date-range')
        today_str = date.today().strftime('%Y-%m-%d')
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        response = api_client.get(url, {
            'start_date': today_str,
            'end_date': tomorrow_str
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


class TestCargoForecastAPI:
    def test_list_cargo_forecasts(self, db):
        client = APIClient()
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        CargoForecast.objects.create(
            warehouse=warehouse,
            date=date.today(),
            predicted_weight=6000,
            confidence=0.85
        )
        
        url = reverse('cargo-forecasts-list')
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        
    def test_create_cargo_forecast(self, db):
        client = APIClient()
        
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        client.force_authenticate(user=admin_user)
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        data = {
            'warehouse': warehouse.id,
            'date': date.today().isoformat(),
            'predicted_weight': 7000,
            'confidence': 0.75
        }
        
        url = reverse('cargo-forecasts-list')
        response = client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert CargoForecast.objects.count() == 1
        
    def test_get_cargo_forecast_detail(self, db):
        client = APIClient()
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        cargo_forecast = CargoForecast.objects.create(
            warehouse=warehouse,
            date=date.today(),
            predicted_weight=8000,
            confidence=0.9
        )
        
        url = reverse('cargo-forecasts-detail', args=[cargo_forecast.id])
        response = client.get(url)
        
        assert response.status_code == 200
        assert response.data['id'] == cargo_forecast.id
        assert response.data['warehouse'] == warehouse.id
        assert response.data['predicted_weight'] == 8000
        assert response.data['confidence'] == 0.9 