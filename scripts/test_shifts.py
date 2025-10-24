"""
Simple script to add test shifts directly to the database
"""
import os
import django
import datetime
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoshift.settings')
django.setup()

from user.models import User
from warehouses.models import Warehouse
from shifts.models import Shift

def add_test_shifts():
    """Add some test shifts for demonstration purposes"""
    
    print("Adding test shifts...")
    
    # Create a basic warehouse if none exists
    warehouse, created = Warehouse.objects.get_or_create(
        name="Test Warehouse 1",
        defaults={"location": "123 Test St"}
    )
    if created:
        print(f"Created warehouse: {warehouse.name}")
    else:
        print(f"Using existing warehouse: {warehouse.name}")
    
    # Create additional warehouses
    warehouse2, created = Warehouse.objects.get_or_create(
        name="Test Warehouse 2",
        defaults={"location": "456 Test Ave"}
    )
    if created:
        print(f"Created warehouse: {warehouse2.name}")
    
    warehouse3, created = Warehouse.objects.get_or_create(
        name="Test Warehouse 3",
        defaults={"location": "789 Test Blvd"}
    )
    if created:
        print(f"Created warehouse: {warehouse3.name}")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            'email': "admin@example.com",
            'role': "admin",
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin_user.set_password("adminpassword")
        admin_user.save()
        print("Created admin user")
    else:
        print("Using existing admin user")
    
    # Create a worker if none exists
    worker, created = User.objects.get_or_create(
        username="worker1",
        defaults={
            'email': "worker1@example.com",
            'role': "worker"
        }
    )
    
    if created:
        worker.set_password("worker1password")
        worker.save()
        print("Created worker user")
    else:
        print("Using existing worker user")
    
    # Create shifts for each day
    shifts_data = [
        # Monday - 3 shifts
        {"day": "monday", "worker": worker, "warehouse": warehouse, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "monday", "worker": worker, "warehouse": warehouse2, "start": (9, 0), "end": (17, 0), "optimized": False},
        {"day": "monday", "worker": worker, "warehouse": warehouse3, "start": (10, 0), "end": (18, 0), "optimized": False},
        
        # Tuesday - 5 shifts
        {"day": "tuesday", "worker": worker, "warehouse": warehouse, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "tuesday", "worker": worker, "warehouse": warehouse, "start": (16, 0), "end": (0, 0), "optimized": False},
        {"day": "tuesday", "worker": worker, "warehouse": warehouse2, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "tuesday", "worker": worker, "warehouse": warehouse2, "start": (16, 0), "end": (0, 0), "optimized": False},
        {"day": "tuesday", "worker": worker, "warehouse": warehouse3, "start": (8, 0), "end": (16, 0), "optimized": False},
        
        # Wednesday - 8 shifts
        {"day": "wednesday", "worker": worker, "warehouse": warehouse, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse, "start": (16, 0), "end": (0, 0), "optimized": False},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse2, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse2, "start": (16, 0), "end": (0, 0), "optimized": True},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse3, "start": (8, 0), "end": (16, 0), "optimized": True},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse3, "start": (16, 0), "end": (0, 0), "optimized": True},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse, "start": (0, 0), "end": (8, 0), "optimized": True},
        {"day": "wednesday", "worker": worker, "warehouse": warehouse2, "start": (0, 0), "end": (8, 0), "optimized": True},
        
        # Thursday - 12 shifts (high count)
        {"day": "thursday", "worker": worker, "warehouse": warehouse, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "thursday", "worker": worker, "warehouse": warehouse, "start": (16, 0), "end": (0, 0), "optimized": False},
        {"day": "thursday", "worker": worker, "warehouse": warehouse, "start": (0, 0), "end": (8, 0), "optimized": False},
        {"day": "thursday", "worker": worker, "warehouse": warehouse2, "start": (8, 0), "end": (16, 0), "optimized": False},
        {"day": "thursday", "worker": worker, "warehouse": warehouse2, "start": (16, 0), "end": (0, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse2, "start": (0, 0), "end": (8, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse3, "start": (8, 0), "end": (16, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse3, "start": (16, 0), "end": (0, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse3, "start": (0, 0), "end": (8, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse, "start": (9, 0), "end": (17, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse2, "start": (9, 0), "end": (17, 0), "optimized": True},
        {"day": "thursday", "worker": worker, "warehouse": warehouse3, "start": (9, 0), "end": (17, 0), "optimized": True},
        
        # Friday - 4 shifts
        {"day": "friday", "worker": worker, "warehouse": warehouse, "start": (8, 0), "end": (16, 0), "optimized": True},
        {"day": "friday", "worker": worker, "warehouse": warehouse, "start": (8, 0), "end": (16, 0), "optimized": True},
        {"day": "friday", "worker": worker, "warehouse": warehouse2, "start": (9, 0), "end": (17, 0), "optimized": True},
        {"day": "friday", "worker": worker, "warehouse": warehouse3, "start": (9, 0), "end": (17, 0), "optimized": False},
        
        # Weekend - fewer shifts
        {"day": "saturday", "worker": worker, "warehouse": warehouse, "start": (10, 0), "end": (18, 0), "optimized": False},
        {"day": "saturday", "worker": worker, "warehouse": warehouse2, "start": (10, 0), "end": (18, 0), "optimized": True},
        {"day": "sunday", "worker": worker, "warehouse": warehouse, "start": (10, 0), "end": (18, 0), "optimized": False},
    ]
    
    # Clear existing shifts
    print("Clearing existing shifts...")
    Shift.objects.all().delete()
    
    # Add the shifts
    for shift_data in shifts_data:
        start_time = datetime.time(shift_data["start"][0], shift_data["start"][1])
        end_time = datetime.time(shift_data["end"][0], shift_data["end"][1])
        
        Shift.objects.create(
            day_of_week=shift_data["day"],
            start_time=start_time,
            end_time=end_time,
            user=shift_data["worker"],
            warehouse=shift_data["warehouse"],
            is_optimized=shift_data["optimized"]
        )
    
    print(f"Added {len(shifts_data)} test shifts")

if __name__ == "__main__":
    add_test_shifts() 