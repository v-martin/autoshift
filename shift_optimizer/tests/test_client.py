import unittest
import sys
import os
import uuid
from unittest.mock import patch, MagicMock, Mock
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from shift_optimizer.client.client import ShiftOptimizerClient


class TestShiftOptimizerClient(unittest.TestCase):
    def setUp(self):
        self.stub_mock = MagicMock()
        
        self.mock_success_response = MagicMock()
        self.mock_success_response.success = True
        self.mock_success_response.message = "Optimization successful"
        self.mock_success_response.shifts = [
            MagicMock(
                worker_uuid=str(uuid.uuid4()),
                warehouse_uuid=str(uuid.uuid4()),
                day_of_week="monday",
                start_time="09:00",
                end_time="17:00"
            ) for _ in range(5)
        ]
        self.mock_success_response.warehouse_staffing = [
            MagicMock(
                warehouse_uuid=str(uuid.uuid4()),
                warehouse_name="Warehouse Test",
                day="monday",
                required_basic_workers=3,
                scheduled_basic_workers=3,
                required_drivers=2,
                scheduled_drivers=2,
                required_engineers=1,
                scheduled_engineers=1,
                is_fully_staffed=True
            ) for _ in range(3)
        ]
        
        self.mock_fail_response = MagicMock()
        self.mock_fail_response.success = False
        self.mock_fail_response.message = "Optimization failed: Not enough workers"
        self.mock_fail_response.shifts = []
        self.mock_fail_response.warehouse_staffing = []
        
        self.worker_uuid = str(uuid.uuid4())
        self.warehouse_uuid = str(uuid.uuid4())
        
        self.mock_workers = [
            self._create_mock_worker(f"worker_{i}") for i in range(5)
        ]
        
        self.mock_warehouses = [
            self._create_mock_warehouse(f"warehouse_{i}") for i in range(3)
        ]
        
        self.mock_cargo_loads = [
            self._create_mock_cargo_load(self.mock_warehouses[i % 3]) for i in range(5)
        ]
        
        self.days = ["monday", "tuesday", "wednesday"]
    
    def _create_mock_worker(self, username):
        mock_worker = MagicMock()
        mock_worker.uuid = str(uuid.uuid4())
        mock_worker.username = username
        
        mock_qualifications = MagicMock()
        mock_qualifications.all.return_value = [
            self._create_mock_qualification("basic_worker", 1),
            self._create_mock_qualification("cargo_driver", 2)
        ]
        mock_worker.qualifications = mock_qualifications
        
        mock_preferences = MagicMock()
        mock_preferences.all.return_value = [
            self._create_mock_warehouse_preference(self.warehouse_uuid)
        ]
        mock_worker.warehouse_preferences = mock_preferences
        
        return mock_worker
    
    def _create_mock_qualification(self, qual_type, level):
        mock_qualification = MagicMock()
        mock_qualification.qualification_type = qual_type
        mock_qualification.level = level
        return mock_qualification
    
    def _create_mock_warehouse_preference(self, warehouse_uuid):
        mock_preference = MagicMock()
        mock_preference.warehouse = MagicMock(uuid=warehouse_uuid)
        mock_preference.priority = 1
        mock_preference.distance = 10.0
        return mock_preference
    
    def _create_mock_warehouse(self, name):
        mock_warehouse = MagicMock()
        mock_warehouse.uuid = str(uuid.uuid4())
        mock_warehouse.name = name
        mock_warehouse.capacity = 1000
        mock_warehouse.min_workers = 3
        mock_warehouse.min_basic_workers = 1
        mock_warehouse.min_drivers = 1
        mock_warehouse.min_engineers = 1
        mock_warehouse.is_active = True
        return mock_warehouse
    
    def _create_mock_cargo_load(self, warehouse):
        mock_cargo = MagicMock()
        mock_cargo.warehouse = warehouse
        mock_cargo.date = MagicMock()
        mock_cargo.date.strftime.return_value = "2025-06-01"
        mock_cargo.total_weight = 1000
        return mock_cargo
    
    @patch('shift_optimizer.client.client.grpc.insecure_channel')
    @patch('shift_optimizer.client.client.shift_optimizer_pb2_grpc.ShiftOptimizerServiceStub')
    def test_init(self, mock_stub_class, mock_channel):
        mock_channel_instance = MagicMock()
        mock_channel.return_value = mock_channel_instance
        
        mock_stub_instance = MagicMock()
        mock_stub_class.return_value = mock_stub_instance
        
        client = ShiftOptimizerClient(host='test_host', port='1234')
        
        mock_channel.assert_called_once_with('test_host:1234')
        
        mock_stub_class.assert_called_once_with(mock_channel_instance)
    
    @patch('shift_optimizer.client.client.grpc.insecure_channel')
    @patch('shift_optimizer.client.client.shift_optimizer_pb2_grpc.ShiftOptimizerServiceStub')
    def test_optimize_shifts_success(self, mock_stub_class, mock_channel):
        mock_channel_instance = MagicMock()
        mock_channel.return_value = mock_channel_instance
        
        mock_stub_instance = MagicMock()
        mock_stub_instance.OptimizeShifts.return_value = self.mock_success_response
        mock_stub_class.return_value = mock_stub_instance
        
        client = ShiftOptimizerClient()
        
        success, message, shifts, staffing = client.optimize_shifts(
            self.mock_workers, 
            self.mock_warehouses, 
            self.mock_cargo_loads, 
            self.days
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Optimization successful")
        self.assertEqual(len(shifts), 5)
        self.assertEqual(len(staffing), 3)
        
        mock_stub_instance.OptimizeShifts.assert_called_once()
    
    @patch('shift_optimizer.client.client.grpc.insecure_channel')
    @patch('shift_optimizer.client.client.shift_optimizer_pb2_grpc.ShiftOptimizerServiceStub')
    def test_optimize_shifts_failure(self, mock_stub_class, mock_channel):
        mock_channel_instance = MagicMock()
        mock_channel.return_value = mock_channel_instance
        
        mock_stub_instance = MagicMock()
        mock_stub_instance.OptimizeShifts.return_value = self.mock_fail_response
        mock_stub_class.return_value = mock_stub_instance
        
        client = ShiftOptimizerClient()
        
        success, message, shifts, staffing = client.optimize_shifts(
            self.mock_workers, 
            self.mock_warehouses, 
            self.mock_cargo_loads, 
            self.days
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Optimization failed: Not enough workers")
        self.assertEqual(len(shifts), 0)
        self.assertEqual(len(staffing), 0)
        
        mock_stub_instance.OptimizeShifts.assert_called_once()
    
    @patch('shift_optimizer.client.client.grpc.insecure_channel')
    @patch('shift_optimizer.client.client.shift_optimizer_pb2_grpc.ShiftOptimizerServiceStub')
    def test_optimize_shifts_exception(self, mock_stub_class, mock_channel):
        mock_channel_instance = MagicMock()
        mock_channel.return_value = mock_channel_instance
        
        mock_stub_instance = MagicMock()
        mock_stub_instance.OptimizeShifts.side_effect = Exception("Test exception")
        mock_stub_class.return_value = mock_stub_instance
        
        client = ShiftOptimizerClient()
        
        success, message, shifts, staffing = client.optimize_shifts(
            self.mock_workers, 
            self.mock_warehouses, 
            self.mock_cargo_loads, 
            self.days
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Error: Test exception")
        self.assertEqual(len(shifts), 0)
        self.assertEqual(len(staffing), 0)
        
        mock_stub_instance.OptimizeShifts.assert_called_once()
if __name__ == "__main__":
    unittest.main() 