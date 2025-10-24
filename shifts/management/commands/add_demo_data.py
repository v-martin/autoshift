from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
import random

from user.models import User
from warehouses.models import Warehouse
from shifts.models import Shift


class Command(BaseCommand):
    help = 'Adds demonstration data for the dashboard'

    def handle(self, *args, **options):
        self.stdout.write("Adding demonstration data for dashboard...")
        
        # Create warehouses
        warehouses = []
        warehouse_names = [
            ("Test Warehouse 1", "123 Test St"),
            ("Test Warehouse 2", "456 Test Ave"),
            ("Test Warehouse 3", "789 Test Blvd"),
        ]
        
        for name, location in warehouse_names:
            warehouse, created = Warehouse.objects.get_or_create(
                name=name,
                defaults={"location": location}
            )
            warehouses.append(warehouse)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created warehouse: {name}"))
            else:
                self.stdout.write(f"Using existing warehouse: {name}")
        
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
            self.stdout.write(self.style.SUCCESS("Created admin user"))
        else:
            self.stdout.write(f"Using existing admin user")
        
        # Create worker
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
            self.stdout.write(self.style.SUCCESS("Created worker user"))
        else:
            self.stdout.write(f"Using existing worker user")
        
        # Clear existing shifts
        self.stdout.write("Clearing existing shifts...")
        Shift.objects.all().delete()
        
        # Create shifts for each day
        shifts_data = [
            # Monday - 3 shifts
            {"day": "monday", "worker": worker, "warehouse": warehouses[0], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "monday", "worker": worker, "warehouse": warehouses[1], "start": (9, 0), "end": (17, 0), "optimized": False},
            {"day": "monday", "worker": worker, "warehouse": warehouses[2], "start": (10, 0), "end": (18, 0), "optimized": False},
            
            # Tuesday - 5 shifts
            {"day": "tuesday", "worker": worker, "warehouse": warehouses[0], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "tuesday", "worker": worker, "warehouse": warehouses[0], "start": (16, 0), "end": (0, 0), "optimized": False},
            {"day": "tuesday", "worker": worker, "warehouse": warehouses[1], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "tuesday", "worker": worker, "warehouse": warehouses[1], "start": (16, 0), "end": (0, 0), "optimized": False},
            {"day": "tuesday", "worker": worker, "warehouse": warehouses[2], "start": (8, 0), "end": (16, 0), "optimized": False},
            
            # Wednesday - 8 shifts
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[0], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[0], "start": (16, 0), "end": (0, 0), "optimized": False},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[1], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[1], "start": (16, 0), "end": (0, 0), "optimized": True},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[2], "start": (8, 0), "end": (16, 0), "optimized": True},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[2], "start": (16, 0), "end": (0, 0), "optimized": True},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[0], "start": (0, 0), "end": (8, 0), "optimized": True},
            {"day": "wednesday", "worker": worker, "warehouse": warehouses[1], "start": (0, 0), "end": (8, 0), "optimized": True},
            
            # Thursday - 12 shifts (high count)
            {"day": "thursday", "worker": worker, "warehouse": warehouses[0], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[0], "start": (16, 0), "end": (0, 0), "optimized": False},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[0], "start": (0, 0), "end": (8, 0), "optimized": False},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[1], "start": (8, 0), "end": (16, 0), "optimized": False},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[1], "start": (16, 0), "end": (0, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[1], "start": (0, 0), "end": (8, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[2], "start": (8, 0), "end": (16, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[2], "start": (16, 0), "end": (0, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[2], "start": (0, 0), "end": (8, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[0], "start": (9, 0), "end": (17, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[1], "start": (9, 0), "end": (17, 0), "optimized": True},
            {"day": "thursday", "worker": worker, "warehouse": warehouses[2], "start": (9, 0), "end": (17, 0), "optimized": True},
            
            # Friday - 4 shifts
            {"day": "friday", "worker": worker, "warehouse": warehouses[0], "start": (8, 0), "end": (16, 0), "optimized": True},
            {"day": "friday", "worker": worker, "warehouse": warehouses[0], "start": (8, 0), "end": (16, 0), "optimized": True},
            {"day": "friday", "worker": worker, "warehouse": warehouses[1], "start": (9, 0), "end": (17, 0), "optimized": True},
            {"day": "friday", "worker": worker, "warehouse": warehouses[2], "start": (9, 0), "end": (17, 0), "optimized": False},
            
            # Weekend - fewer shifts
            {"day": "saturday", "worker": worker, "warehouse": warehouses[0], "start": (10, 0), "end": (18, 0), "optimized": False},
            {"day": "saturday", "worker": worker, "warehouse": warehouses[1], "start": (10, 0), "end": (18, 0), "optimized": True},
            {"day": "sunday", "worker": worker, "warehouse": warehouses[0], "start": (10, 0), "end": (18, 0), "optimized": False},
        ]
        
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
        
        self.stdout.write(self.style.SUCCESS(f"Added {len(shifts_data)} demonstration shifts"))
        self.stdout.write(self.style.SUCCESS("Now visit http://localhost:8000/dashboard/ to see the dashboard")) 