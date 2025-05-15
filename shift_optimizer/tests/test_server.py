import unittest
import uuid
import sys
import os
from datetime import datetime
from unittest.mock import patch
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from shift_optimizer.server.models import Worker, Warehouse, CargoLoad, Qualification
from shift_optimizer.server.optimizer import ShiftOptimizer
class TestShiftOptimizer(unittest.TestCase):
    def setUp(self):
        self.basic_qualification = Qualification(type='BASIC_WORKER', level=1)
        self.driver_qualification = Qualification(type='CARGO_DRIVER', level=2)
        self.engineer_qualification = Qualification(type='ENGINEER', level=3)
        
        self.workers = [
            Worker(
                uuid=str(uuid.uuid4()),
                username=f"worker_{i}",
                qualifications=[
                    self.basic_qualification if i % 3 == 0 else None,
                    self.driver_qualification if i % 3 == 1 else None,
                    self.engineer_qualification if i % 3 == 2 else None
                ],
                warehouse_preferences=[]
            ) for i in range(10)
        ]
        
        for worker in self.workers:
            worker.qualifications = [q for q in worker.qualifications if q is not None]
        
        self.warehouses = [
            Warehouse(
                uuid=str(uuid.uuid4()),
                name=f"warehouse_{i}",
                capacity=1000 * (i + 1),
                min_workers=3,
                min_basic_workers=1,
                min_drivers=1,
                min_engineers=1,
                is_active=True
            ) for i in range(3)
        ]
        
        self.cargo_loads = [
            CargoLoad(
                warehouse_uuid=warehouse.uuid,
                date="2023-06-01",
                total_weight=500 * (i + 1)
            ) for i, warehouse in enumerate(self.warehouses)
        ]
        
        for i, worker in enumerate(self.workers):
            worker.warehouse_preferences = [
                {
                    "warehouse_uuid": self.warehouses[i % 3].uuid,
                    "priority": 1,
                    "distance": 10.0
                }
            ]
        
        self.days = ["monday", "tuesday", "wednesday"]
        
        self.optimizer = ShiftOptimizer(
            workers=self.workers,
            warehouses=self.warehouses,
            cargo_loads=self.cargo_loads,
            days=self.days
        )
    
    def test_worker_qualifications(self):
        basic_workers = [w for w in self.workers if any(q.type == 'BASIC_WORKER' for q in w.qualifications)]
        self.assertGreater(len(basic_workers), 0)
        
        drivers = [w for w in self.workers if any(q.type == 'CARGO_DRIVER' for q in w.qualifications)]
        self.assertGreater(len(drivers), 0)
        
        engineers = [w for w in self.workers if any(q.type == 'ENGINEER' for q in w.qualifications)]
        self.assertGreater(len(engineers), 0)
        
        day = self.days[0]
        warehouse_uuid = self.warehouses[0].uuid
        
        requirements = {
            'scheduled_basic_workers': 0,
            'scheduled_drivers': 0,
            'scheduled_engineers': 0
        }
        
        self.optimizer.shifts = []
        self.optimizer.scheduled_workers = {d: set() for d in self.days}
        
        self.optimizer._assign_workers_by_qualification(
            basic_workers[:2], day, warehouse_uuid, 'BASIC_WORKER', 2, requirements
        )
        
        self.assertEqual(requirements['scheduled_basic_workers'], 2)
        self.assertEqual(len(self.optimizer.shifts), 2)
        
        self.assertEqual(len(self.optimizer.scheduled_workers[day]), 2)
        
        assigned_worker_uuids = list(self.optimizer.scheduled_workers[day])
        assigned_workers = [w for w in self.workers if w.uuid in assigned_worker_uuids]
        
        orig_shifts_count = len(self.optimizer.shifts)
        self.optimizer._assign_workers_by_qualification(
            assigned_workers, day, warehouse_uuid, 'BASIC_WORKER', 2, requirements
        )
        
        self.assertEqual(len(self.optimizer.shifts), orig_shifts_count)
    
    def test_calculate_warehouse_requirements(self):
        requirements = self.optimizer._calculate_warehouse_requirements()
        
        for day in self.days:
            self.assertIn(day, requirements)
            
            self.assertTrue(isinstance(requirements[day], dict))
            
            for warehouse in self.warehouses:
                self.assertIn(warehouse.uuid, requirements[day])
                
                day_req = requirements[day][warehouse.uuid]
                
                self.assertIn("warehouse_uuid", day_req)
                self.assertIn("warehouse_name", day_req)
                self.assertIn("min_basic_workers", day_req)
                self.assertIn("min_drivers", day_req)
                self.assertIn("min_engineers", day_req)
                self.assertIn("total_basic_workers", day_req)
                self.assertIn("total_drivers", day_req)
                self.assertIn("total_engineers", day_req)
                self.assertIn("scheduled_basic_workers", day_req)
                self.assertIn("scheduled_drivers", day_req)
                self.assertIn("scheduled_engineers", day_req)
                
                self.assertEqual(day_req["warehouse_uuid"], warehouse.uuid)
                self.assertEqual(day_req["warehouse_name"], warehouse.name)
                self.assertEqual(day_req["min_basic_workers"], warehouse.min_basic_workers)
                self.assertEqual(day_req["min_drivers"], warehouse.min_drivers)
                self.assertEqual(day_req["min_engineers"], warehouse.min_engineers)
                
                self.assertGreaterEqual(day_req["total_basic_workers"], warehouse.min_basic_workers)
                self.assertGreaterEqual(day_req["total_drivers"], warehouse.min_drivers)
                self.assertGreaterEqual(day_req["total_engineers"], warehouse.min_engineers)
                
                self.assertEqual(day_req["scheduled_basic_workers"], 0)
                self.assertEqual(day_req["scheduled_drivers"], 0)
                self.assertEqual(day_req["scheduled_engineers"], 0)
    
    def test_sort_workers_by_preference(self):
        warehouse_uuid = self.warehouses[0].uuid
        sorted_workers = self.optimizer._sort_workers_by_preference(warehouse_uuid)
        
        self.assertGreater(len(sorted_workers), 0)
        
        for worker in sorted_workers:
            self.assertIsInstance(worker, Worker)
        
        has_preference = False
        for worker in sorted_workers:
            for pref in worker.warehouse_preferences:
                if pref["warehouse_uuid"] == warehouse_uuid:
                    has_preference = True
                    break
            
            if has_preference:
                break
                
        self.assertTrue(has_preference, "No workers with preference for this warehouse found")
    
    def test_assign_minimum_staff(self):
        requirements = self.optimizer._calculate_warehouse_requirements()
        
        self.optimizer.shifts = []
        self.optimizer.scheduled_workers = {day: set() for day in self.days}
        
        self.optimizer._assign_minimum_staff(requirements)
        
        self.assertGreater(len(self.optimizer.shifts), 0)
        
        shifts_by_warehouse = {}
        for shift in self.optimizer.shifts:
            warehouse_uuid = shift.warehouse_uuid
            if warehouse_uuid not in shifts_by_warehouse:
                shifts_by_warehouse[warehouse_uuid] = []
            shifts_by_warehouse[warehouse_uuid].append(shift)
        
        for warehouse in self.warehouses:
            self.assertIn(warehouse.uuid, shifts_by_warehouse)
            warehouse_shifts = shifts_by_warehouse[warehouse.uuid]
            
            min_total = warehouse.min_basic_workers + warehouse.min_drivers + warehouse.min_engineers
            self.assertGreaterEqual(len(warehouse_shifts), min_total)
            
            for day in self.days:
                day_shifts = [s for s in warehouse_shifts if s.day_of_week == day]
                self.assertGreater(len(day_shifts), 0)
    
    def test_generate_staffing_reports(self):
        shifts, staffing = self.optimizer.optimize()
        
        self.assertGreater(len(staffing), 0)
        
        reported_warehouses = set()
        reported_days = set()
        
        for staff_report in staffing:
            reported_warehouses.add(staff_report.warehouse_uuid)
            reported_days.add(staff_report.day)
            
            self.assertIsNotNone(staff_report.required_basic_workers)
            self.assertIsNotNone(staff_report.scheduled_basic_workers)
            self.assertIsNotNone(staff_report.required_drivers)
            self.assertIsNotNone(staff_report.scheduled_drivers)
            self.assertIsNotNone(staff_report.required_engineers)
            self.assertIsNotNone(staff_report.scheduled_engineers)
            self.assertIsNotNone(staff_report.is_fully_staffed)
        
        for warehouse in self.warehouses:
            self.assertIn(warehouse.uuid, reported_warehouses)
            
        for day in self.days:
            self.assertIn(day, reported_days)
    
    def test_optimize(self):
        shifts, staffing = self.optimizer.optimize()
        
        self.assertGreater(len(shifts), 0)
        
        self.assertGreater(len(staffing), 0)
        
        assigned_workers = set()
        for shift in shifts:
            assigned_workers.add(shift.worker_uuid)
            
            self.assertIsNotNone(shift.warehouse_uuid)
            self.assertIsNotNone(shift.day_of_week)
            self.assertIsNotNone(shift.start_time)
            self.assertIsNotNone(shift.end_time)
        
        min_workers_required = min(len(self.workers), sum(w.min_workers for w in self.warehouses))
        self.assertGreaterEqual(len(assigned_workers), min_workers_required)
if __name__ == "__main__":
    unittest.main() 