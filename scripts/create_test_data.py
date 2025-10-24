#!/usr/bin/env python
import os
import django
import random
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoshift.settings')
django.setup()

from django.utils import timezone
from user.models import User
from warehouses.models import Warehouse
from shifts.models import Shift

def create_test_data():
    print("Creating test data for AutoShift dashboard...")
    
    # Create warehouses
    warehouses = []
    warehouse_names = [
        ("North Warehouse", "123 North St"),
        ("South Warehouse", "456 South St"),
        ("East Warehouse", "789 East St"),
        ("West Warehouse", "321 West St"),
        ("Central Warehouse", "555 Main St")
    ]
    
    for name, location in warehouse_names:
        warehouse, created = Warehouse.objects.get_or_create(
            name=name,
            defaults={'location': location}
        )
        warehouses.append(warehouse)
        if created:
            print(f"Created warehouse: {name}")
        else:
            print(f"Using existing warehouse: {name}")
    
    # Create users
    admin_user, admin_created = User.objects.get_or_create(
        username="admin",
        defaults={
            'email': "admin@example.com",
            'role': "admin",
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if admin_created:
        admin_user.set_password("adminpassword")
        admin_user.save()
        print("Created admin user")
    else:
        print("Using existing admin user")
    
    # Create workers
    workers = []
    for i in range(1, 11):
        worker, created = User.objects.get_or_create(
            username=f"worker{i}",
            defaults={
                'email': f"worker{i}@example.com",
                'role': "worker"
            }
        )
        
        if created:
            worker.set_password(f"worker{i}password")
            worker.save()
            print(f"Created worker: worker{i}")
        else:
            print(f"Using existing worker: worker{i}")
            
        workers.append(worker)
    
    # Create shifts
    # Define shift time slots
    time_slots = [
        (datetime.time(6, 0), datetime.time(14, 0)),  # Morning shift
        (datetime.time(14, 0), datetime.time(22, 0)), # Afternoon shift
        (datetime.time(22, 0), datetime.time(6, 0)),  # Night shift
        (datetime.time(9, 0), datetime.time(17, 0)),  # Standard day shift
    ]
    
    # Days of the week
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    # Clear existing shifts to avoid duplication
    if input("Do you want to clear existing shifts? (y/n): ").lower() == 'y':
        Shift.objects.all().delete()
        print("Cleared existing shifts")
    
    # Create a varied distribution of shifts
    shift_count = 0
    for day in days:
        # Add more shifts for weekdays, fewer for weekends
        num_shifts = 15 if day not in ["saturday", "sunday"] else 8
        
        for _ in range(num_shifts):
            worker = random.choice(workers)
            warehouse = random.choice(warehouses)
            start_time, end_time = random.choice(time_slots)
            
            # Randomly decide if the shift is optimized
            is_optimized = random.random() < 0.3  # 30% chance of being optimized
            
            Shift.objects.create(
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                user=worker,
                warehouse=warehouse,
                is_optimized=is_optimized
            )
            shift_count += 1
    
    print(f"Created {shift_count} shifts")
    print("Test data creation complete!")

if __name__ == "__main__":
    create_test_data() 