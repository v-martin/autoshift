import pytest
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User, WorkerQualification, WorkerWarehousePreference
from warehouses.models import Warehouse

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


class TestAuthenticationAPI:
    def test_signup(self, db):
        client = APIClient()
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@example.com').exists()
        
    def test_signin(self, db):
        client = APIClient()
        # Create a user first
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        url = reverse('signin')
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        
    def test_signin_invalid_credentials(self, db):
        client = APIClient()
        # Create a user first
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        url = reverse('signin')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_token_auth(self, api_client):
        # Create a user first
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data


class TestUserAPI:
    @pytest.fixture
    def setup_qualification(self, worker_user):
        return WorkerQualification.objects.create(
            user=worker_user,
            qualification_type=WorkerQualification.BASIC_WORKER,
            level=3
        )
    
    @pytest.fixture
    def setup_preference(self, worker_user, warehouse):
        return WorkerWarehousePreference.objects.create(
            user=worker_user,
            warehouse=warehouse,
            priority=1
        )
    
    def test_worker_list(self, api_client, admin_user, worker_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('workers')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # Just the worker user
        
    def test_profile_me(self, api_client, worker_user):
        api_client.force_authenticate(user=worker_user)
        url = reverse('profile-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == worker_user.username
        assert response.data['email'] == worker_user.email
        
    def test_update_profile(self, api_client, worker_user):
        api_client.force_authenticate(user=worker_user)
        url = reverse('profile-update-profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Worker'
        }
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh from database
        worker_user.refresh_from_db()
        assert worker_user.first_name == 'Updated'
        assert worker_user.last_name == 'Worker'
        
    def test_get_qualifications(self, api_client, worker_user, setup_qualification):
        api_client.force_authenticate(user=worker_user)
        url = reverse('profile-get-qualifications')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['qualification_type'] == WorkerQualification.BASIC_WORKER
        
    def test_worker_qualifications_crud(self, api_client, worker_user, setup_qualification):
        api_client.force_authenticate(user=worker_user)
        
        # List qualifications
        url = reverse('user-qualifications-list', args=[worker_user.uuid])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        
        # Create qualification
        data = {
            'qualification_type': WorkerQualification.CARGO_DRIVER,
            'level': 2
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify count increased
        response = api_client.get(url)
        assert len(response.data) == 2
        
        # Update qualification
        qualification_id = WorkerQualification.objects.get(
            user=worker_user, 
            qualification_type=WorkerQualification.CARGO_DRIVER
        ).id
        update_url = reverse('user-qualifications-detail', args=[worker_user.uuid, qualification_id])
        update_data = {'level': 4}
        response = api_client.patch(update_url, update_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify update worked
        qualification = WorkerQualification.objects.get(id=qualification_id)
        assert qualification.level == 4
        
        # Delete qualification
        response = api_client.delete(update_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        response = api_client.get(url)
        assert len(response.data) == 1

    def test_list_users(self, db):
        client = APIClient()
        
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        User.objects.create_user(
            username="worker1",
            email="worker1@example.com",
            password="password123"
        )
        
        client.force_authenticate(user=admin_user)
        url = reverse('users-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
    def test_get_user_detail(self, db):
        client = APIClient()
        
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        client.force_authenticate(user=admin_user)
        url = reverse('users-detail', args=[user.id])
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == "testuser"
        assert response.data['email'] == "test@example.com"
        
    def test_create_worker_qualification(self, db):
        client = APIClient()
        
        worker = User.objects.create_user(
            username="worker",
            email="worker@example.com",
            password="password123"
        )
        
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        client.force_authenticate(user=admin_user)
        
        url = reverse('worker-qualifications-list')
        data = {
            'user': worker.id,
            'qualification_type': WorkerQualification.BASIC_WORKER,
            'level': 3
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert WorkerQualification.objects.count() == 1
        
    def test_create_warehouse_preference(self, db):
        client = APIClient()
        
        worker = User.objects.create_user(
            username="worker",
            email="worker@example.com",
            password="password123"
        )
        
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        client.force_authenticate(user=worker)
        
        url = reverse('worker-preferences-list')
        data = {
            'warehouse': warehouse.id,
            'priority': 1,
            'distance': 5.5
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert WorkerWarehousePreference.objects.count() == 1 