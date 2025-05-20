import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from user.models import User
from warehouses.models import Warehouse


class TestWarehouseModel:
    def test_warehouse_creation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50,
            min_workers=5,
            min_basic_workers=2,
            min_drivers=2,
            min_engineers=1
        )
        
        assert isinstance(warehouse, Warehouse)
        assert str(warehouse) == "Test Warehouse"
        assert warehouse.capacity == 50
        assert warehouse.min_workers == 5
        assert warehouse.min_basic_workers == 2
        assert warehouse.min_drivers == 2
        assert warehouse.min_engineers == 1
        assert warehouse.is_active == True


class TestWarehouseAPI:
    @pytest.fixture
    def setup(self, db):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            is_staff=True
        )
        self.warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50,
            min_workers=5,
            min_basic_workers=2,
            min_drivers=2,
            min_engineers=1
        )
        self.client.force_authenticate(user=self.admin_user)
        
    def test_list_warehouses(self, db, setup):
        url = reverse('warehouse-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        
    def test_retrieve_warehouse(self, db, setup):
        url = reverse('warehouse-detail', args=[self.warehouse.id])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == "Test Warehouse"
        assert response.data['capacity'] == 50
        
    def test_create_warehouse(self, db, setup):
        url = reverse('warehouse-list')
        data = {
            'name': 'New Warehouse',
            'address': '456 New St',
            'capacity': 100,
            'min_workers': 10,
            'min_basic_workers': 5,
            'min_drivers': 3,
            'min_engineers': 2
        }
        response = self.client.post(url, data)
        assert response.status_code == 201
        assert Warehouse.objects.count() == 2
        
        # Verify the data was saved correctly
        new_warehouse = Warehouse.objects.get(name='New Warehouse')
        assert new_warehouse.capacity == 100
        assert new_warehouse.min_workers == 10
        
    def test_update_warehouse(self, db, setup):
        url = reverse('warehouse-detail', args=[self.warehouse.id])
        data = {
            'name': 'Updated Warehouse',
            'address': self.warehouse.address,
            'capacity': 75,
            'min_workers': self.warehouse.min_workers,
            'min_basic_workers': self.warehouse.min_basic_workers,
            'min_drivers': self.warehouse.min_drivers,
            'min_engineers': self.warehouse.min_engineers
        }
        response = self.client.put(url, data)
        assert response.status_code == 200
        
        # Refresh from database
        self.warehouse.refresh_from_db()
        assert self.warehouse.name == "Updated Warehouse"
        assert self.warehouse.capacity == 75
        
    def test_partial_update_warehouse(self, db, setup):
        url = reverse('warehouse-detail', args=[self.warehouse.id])
        data = {
            'name': 'Partially Updated Warehouse'
        }
        response = self.client.patch(url, data)
        assert response.status_code == 200
        
        # Refresh from database
        self.warehouse.refresh_from_db()
        assert self.warehouse.name == "Partially Updated Warehouse"
        # Original value should remain unchanged
        assert self.warehouse.capacity == 50
        
    def test_deactivate_warehouse(self, db, setup):
        url = reverse('warehouse-detail', args=[self.warehouse.id])
        data = {
            'is_active': False
        }
        response = self.client.patch(url, data)
        assert response.status_code == 200
        
        # Refresh from database
        self.warehouse.refresh_from_db()
        assert self.warehouse.is_active == False 