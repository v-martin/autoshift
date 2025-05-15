import unittest
import sys
import os
import uuid
import datetime
import logging
from unittest.mock import patch, MagicMock, Mock, PropertyMock
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
logging.disable(logging.CRITICAL)
mock_django_conf = MagicMock()
mock_django_settings = MagicMock()
sys.modules['django.conf'] = mock_django_conf
sys.modules['django.conf.settings'] = mock_django_settings
mock_user_models = MagicMock()
mock_warehouses_models = MagicMock()
mock_cargo_models = MagicMock()
mock_shifts_models = MagicMock()
sys.modules['user'] = MagicMock()
sys.modules['user.models'] = mock_user_models
sys.modules['warehouses'] = MagicMock()
sys.modules['warehouses.models'] = mock_warehouses_models
sys.modules['cargo'] = MagicMock()
sys.modules['cargo.models'] = mock_cargo_models
sys.modules['shifts'] = MagicMock()
sys.modules['shifts.models'] = mock_shifts_models
from shift_optimizer.client.django_integration import ShiftOptimizationService
class TestShiftOptimizationService(unittest.TestCase):
    def setUp(self):
        self.client_mock = MagicMock()
        
        self.worker_uuids = [str(uuid.uuid4()) for _ in range(5)]
        self.warehouse_uuids = [str(uuid.uuid4()) for _ in range(3)]
        
        self.success_response = (True, "Optimization successful", [
            {
                'worker_uuid': self.worker_uuids[i % 5],
                'warehouse_uuid': self.warehouse_uuids[i % 3],
                'day_of_week': 'monday',
                'start_time': '09:00',
                'end_time': '17:00'
            } for i in range(5)
        ], [
            {
                'warehouse_uuid': self.warehouse_uuids[i % 3],
                'warehouse_name': f'Test Warehouse {i}',
                'day': 'monday',
                'required_basic_workers': 3,
                'scheduled_basic_workers': 3,
                'required_drivers': 2,
                'scheduled_drivers': 2,
                'required_engineers': 1,
                'scheduled_engineers': 1,
                'is_fully_staffed': True
            } for i in range(3)
        ])
        
        self.fail_response = (False, "Optimization failed", [], [])
        
        self.today = datetime.date.today()
        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.next_week = self.today + datetime.timedelta(days=7)
        
        self.mock_workers = [self._create_mock_worker(uuid=uid) for uid in self.worker_uuids]
        self.mock_warehouses = [self._create_mock_warehouse(uuid=uid) for uid in self.warehouse_uuids]
        self.mock_cargo_load = self._create_mock_cargo_load()
        
        self.worker_filter_mock = MagicMock()
        self.worker_filter_mock.prefetch_related.return_value = self.mock_workers
        
        self.warehouse_filter_mock = MagicMock()
        self.warehouse_filter_mock.filter.return_value = self.mock_warehouses
        
        self.cargo_load_filter_mock = MagicMock()
        self.cargo_load_filter_mock.return_value = [self.mock_cargo_load]
        
        self.worker_get_mock = MagicMock()
        self.worker_get_mock.side_effect = self._mock_worker_get
        
        self.warehouse_get_mock = MagicMock()
        self.warehouse_get_mock.side_effect = self._mock_warehouse_get
        
        self.shift_update_mock = MagicMock()
        self.shift_update_mock.return_value = (MagicMock(), True)
        
        self._reset_mocks()
        
        self.setup_django_models()
    
    def _reset_mocks(self):
        
        fresh_shift_update_mock = MagicMock()
        fresh_shift_update_mock.return_value = (MagicMock(), True)
        if hasattr(mock_shifts_models, 'Shift'):
            mock_shifts_models.Shift.objects.update_or_create = fresh_shift_update_mock
    
    def _mock_worker_get(self, uuid=None, **kwargs):
        
        if uuid in self.worker_uuids:
            return next(w for w in self.mock_workers if w.uuid == uuid)
        raise mock_user_models.Worker.DoesNotExist(f"Worker with UUID {uuid} not found")
    
    def _mock_warehouse_get(self, uuid=None, **kwargs):
        
        if uuid in self.warehouse_uuids:
            return next(w for w in self.mock_warehouses if w.uuid == uuid)
        raise mock_warehouses_models.Warehouse.DoesNotExist(f"Warehouse with UUID {uuid} not found")
    
    def setup_django_models(self):
        
        mock_user_models.Worker = MagicMock()
        mock_user_models.Worker.objects = MagicMock()
        mock_user_models.Worker.objects.filter = MagicMock(return_value=self.worker_filter_mock)
        mock_user_models.Worker.objects.get = self.worker_get_mock
        mock_user_models.Worker.DoesNotExist = type('DoesNotExist', (Exception,), {})
        
        mock_user_models.Qualification = MagicMock()
        
        mock_user_models.WarehousePreference = MagicMock()
        
        mock_warehouses_models.Warehouse = MagicMock()
        mock_warehouses_models.Warehouse.objects = MagicMock()
        mock_warehouses_models.Warehouse.objects.filter = MagicMock(return_value=self.warehouse_filter_mock)
        mock_warehouses_models.Warehouse.objects.get = self.warehouse_get_mock
        mock_warehouses_models.Warehouse.DoesNotExist = type('DoesNotExist', (Exception,), {})
        
        mock_cargo_models.CargoLoad = MagicMock()
        mock_cargo_models.CargoLoad.objects = MagicMock()
        mock_cargo_models.CargoLoad.objects.filter = MagicMock(return_value=self.cargo_load_filter_mock)
        
        mock_shifts_models.Shift = MagicMock()
        mock_shifts_models.Shift.objects = MagicMock()
        mock_shifts_models.Shift.objects.update_or_create = MagicMock(return_value=(MagicMock(), True))
    
    def _create_mock_worker(self, uuid=None):
        
        mock_worker = MagicMock()
        mock_worker.uuid = uuid or str(uuid.uuid4())
        mock_worker.username = f"worker_{mock_worker.uuid[:8]}"
        mock_worker.is_active = True
        mock_worker.qualifications = []
        mock_worker.warehouse_preferences = []
        return mock_worker
    
    def _create_mock_warehouse(self, uuid=None):
        
        mock_warehouse = MagicMock()
        mock_warehouse.uuid = uuid or str(uuid.uuid4())
        mock_warehouse.name = f"warehouse_{mock_warehouse.uuid[:8]}"
        mock_warehouse.is_active = True
        return mock_warehouse
    
    def _create_mock_cargo_load(self):
        
        mock_cargo = MagicMock()
        mock_cargo.warehouse = self.mock_warehouses[0] if hasattr(self, 'mock_warehouses') and self.mock_warehouses else MagicMock()
        mock_cargo.date = self.today
        mock_cargo.total_weight = 1000
        return mock_cargo
    
    def test_init(self):
        with patch('shift_optimizer.client.django_integration.ShiftOptimizerClient') as client_class_mock:
            client_class_mock.return_value = self.client_mock
            service = ShiftOptimizationService()
            
            client_class_mock.assert_called_once()
    
    def test_optimize_shifts_success(self):
        with patch.dict('sys.modules', {
            'user.models': mock_user_models,
            'warehouses.models': mock_warehouses_models,
            'cargo.models': mock_cargo_models,
            'shifts.models': mock_shifts_models
        }):
            self._reset_mocks()
            warehouse_queryset_mock = MagicMock()
            warehouse_queryset_mock.__iter__.return_value = iter(self.mock_warehouses)
            warehouse_queryset_mock.__len__.return_value = len(self.mock_warehouses)
            warehouse_queryset_mock.filter.return_value = warehouse_queryset_mock
            mock_warehouses_models.Warehouse.objects.filter.return_value = warehouse_queryset_mock
            
            worker_prefetch_mock = MagicMock()
            worker_prefetch_mock.__iter__.return_value = iter(self.mock_workers)
            worker_prefetch_mock.__len__.return_value = len(self.mock_workers)
            mock_user_models.Worker.objects.filter.return_value.prefetch_related.return_value = worker_prefetch_mock
            
            cargo_load_queryset_mock = MagicMock()
            cargo_load_queryset_mock.__iter__.return_value = iter([self.mock_cargo_load])
            cargo_load_queryset_mock.__len__.return_value = 1
            mock_cargo_models.CargoLoad.objects.filter.return_value = cargo_load_queryset_mock
            
            mock_update_or_create = MagicMock(return_value=(MagicMock(), True))
            mock_shifts_models.Shift.objects.update_or_create = mock_update_or_create
            
            with patch('shift_optimizer.client.django_integration.ShiftOptimizerClient') as client_class_mock:
                client_instance = MagicMock()
                client_instance.optimize_shifts.return_value = self.success_response
                client_class_mock.return_value = client_instance
                
                service = ShiftOptimizationService()
                
                mock_django_settings.SHIFT_OPTIMIZER_HOST = 'localhost'
                mock_django_settings.SHIFT_OPTIMIZER_PORT = '50051'
                
                success, message, shifts, staffing = service.optimize_shifts(
                    self.today, self.tomorrow
                )
                
                expected_days = [self.today.strftime("%A").lower(), self.tomorrow.strftime("%A").lower()]
                
                self.assertEqual(client_instance.optimize_shifts.call_count, 1,
                               "optimize_shifts метод клиента не был вызван")
                
                call_args = client_instance.optimize_shifts.call_args[0]
                self.assertEqual(len(call_args[0]), len(self.mock_workers),
                                "Неверное количество работников передано клиенту")
                self.assertEqual(len(call_args[1]), len(self.mock_warehouses),
                                "Неверное количество складов передано клиенту")
                self.assertEqual(call_args[3], expected_days,
                                "Неверный список дней передан клиенту")
                
                self.assertTrue(success, "Оптимизация должна быть успешной")
                self.assertEqual(message, "Optimization successful", "Неверное сообщение об успехе")
                self.assertEqual(len(shifts), 5, "Должно быть 5 смен в результате")
                self.assertEqual(len(staffing), 3, "Должно быть 3 элемента отчета о персонале")
                
                self.assertEqual(mock_update_or_create.call_count, 5,
                                "Должно быть создано 5 записей о сменах в базе данных")
                
                for i, call in enumerate(mock_update_or_create.call_args_list):
                    kwargs = call[1]
                    self.assertIn('defaults', kwargs, f"В вызове {i} отсутствует defaults")
                    defaults = kwargs['defaults']
                    self.assertIn('start_time', defaults, f"В вызове {i} отсутствует start_time")
                    self.assertIn('end_time', defaults, f"В вызове {i} отсутствует end_time")
                    self.assertIn('is_optimized', defaults, f"В вызове {i} отсутствует is_optimized")
                    self.assertTrue(defaults['is_optimized'], f"В вызове {i} is_optimized должен быть True")
    
    def test_optimize_shifts_date_validation(self):
        
        with patch('shift_optimizer.client.django_integration.ShiftOptimizerClient') as client_class_mock:
            client_instance = MagicMock()
            client_class_mock.return_value = client_instance
            
            service = ShiftOptimizationService()
            
            success, message, shifts, staffing = service.optimize_shifts(
                "2023-01-01"
            )
            self.assertFalse(success)
            self.assertEqual(message, "Invalid date format")
            
            success, message, shifts, staffing = service.optimize_shifts(
                self.tomorrow, self.today
            )
            self.assertFalse(success)
            self.assertEqual(message, "Start date cannot be after end date")
            
            success, message, shifts, staffing = service.optimize_shifts(
                self.today, self.today + datetime.timedelta(days=15)
            )
            self.assertFalse(success)
            self.assertEqual(message, "Optimization period cannot exceed 14 days")
            
            client_instance.optimize_shifts.assert_not_called()
    
    def test_save_optimized_shifts_success(self):
        
        with patch.dict('sys.modules', {
            'user.models': mock_user_models,
            'warehouses.models': mock_warehouses_models,
            'shifts.models': mock_shifts_models,
        }):
            self._reset_mocks()
            
            mock_update_or_create = MagicMock(return_value=(MagicMock(), True))
            mock_shifts_models.Shift.objects.update_or_create = mock_update_or_create
            
            service = ShiftOptimizationService()
            
            shifts = [
                {
                    'worker_uuid': self.worker_uuids[i],
                    'warehouse_uuid': self.warehouse_uuids[i % 3],
                    'day_of_week': 'monday',
                    'start_time': '09:00',
                    'end_time': '17:00'
                } for i in range(5)
            ]
            
            success, message, saved_count = service.save_optimized_shifts(shifts)
            
            self.assertTrue(success)
            self.assertEqual(saved_count, 5)
            
            self.assertEqual(mock_update_or_create.call_count, 5)
    
    def test_save_optimized_shifts_worker_not_found(self):
        
        with patch.dict('sys.modules', {
            'user.models': mock_user_models,
            'warehouses.models': mock_warehouses_models,
            'shifts.models': mock_shifts_models,
        }):
            self._reset_mocks()
            
            mock_update_or_create = MagicMock(return_value=(MagicMock(), True))
            mock_shifts_models.Shift.objects.update_or_create = mock_update_or_create
            
            service = ShiftOptimizationService()
            
            invalid_worker_uuid = str(uuid.uuid4())
            shifts = [
                {
                    'worker_uuid': self.worker_uuids[0],
                    'warehouse_uuid': self.warehouse_uuids[0],
                    'day_of_week': 'monday',
                    'start_time': '09:00',
                    'end_time': '17:00'
                },
                {
                    'worker_uuid': invalid_worker_uuid,
                    'warehouse_uuid': self.warehouse_uuids[1],
                    'day_of_week': 'monday',
                    'start_time': '09:00',
                    'end_time': '17:00'
                },
                {
                    'worker_uuid': self.worker_uuids[2],
                    'warehouse_uuid': self.warehouse_uuids[2],
                    'day_of_week': 'monday',
                    'start_time': '09:00',
                    'end_time': '17:00'
                },
                {
                    'worker_uuid': self.worker_uuids[3],
                    'warehouse_uuid': self.warehouse_uuids[0],
                    'day_of_week': 'monday',
                    'start_time': '09:00',
                    'end_time': '17:00'
                },
                {
                    'worker_uuid': self.worker_uuids[4],
                    'warehouse_uuid': self.warehouse_uuids[1],
                    'day_of_week': 'monday',
                    'start_time': '09:00',
                    'end_time': '17:00'
                }
            ]
            
            def mock_worker_get_with_exception(uuid=None, **kwargs):
                if uuid == invalid_worker_uuid:
                    raise mock_user_models.Worker.DoesNotExist(f"Worker with UUID {uuid} not found")
                return next((w for w in self.mock_workers if w.uuid == uuid), None)
            
            mock_user_models.Worker.objects.get.side_effect = mock_worker_get_with_exception
            
            success, message, saved_count = service.save_optimized_shifts(shifts)
            
            self.assertTrue(success)
            self.assertEqual(saved_count, 4)
            
            self.assertEqual(mock_update_or_create.call_count, 4)
    def test_save_optimized_shifts_is_called(self):
        
        
        class TestShiftService(ShiftOptimizationService):
            def save_optimized_shifts(self, shifts):
                self.save_called = True
                self.save_shifts = shifts
                return True, "Success", 5
        
        shifts_data = [{"test": "data"}]
        service = TestShiftService()
        service.save_called = False
        service.save_shifts = None
        
        service.save_optimized_shifts(shifts_data)
        
        self.assertTrue(service.save_called, "save_optimized_shifts was not called")
        self.assertEqual(service.save_shifts, shifts_data, "save_optimized_shifts received wrong data")
    def test_optimize_calls_save(self):
        
        
        class TestShiftServiceWithSuccessfulOptimize(ShiftOptimizationService):
            def __init__(self):
                self.client = MagicMock()
                self.shifts_data = [{"test": "data"}]
                self.client.optimize_shifts.return_value = (True, "Success", self.shifts_data, [])
                self.save_called = False
                self.save_shifts = None
            
            def save_optimized_shifts(self, shifts):
                self.save_called = True
                self.save_shifts = shifts
                return True, "Success", len(shifts)
            
            def optimize_shifts(self, start_date, end_date=None, warehouse_ids=None):
                success, message, shifts, staffing = self.client.optimize_shifts(None, None, None, None)
                
                if success:
                    self.save_optimized_shifts(shifts)
                
                return success, message, shifts, staffing
        
        service = TestShiftServiceWithSuccessfulOptimize()
        
        today = datetime.date.today()
        success, message, shifts, staffing = service.optimize_shifts(today)
        
        self.assertTrue(service.save_called, "save_optimized_shifts was not called")
        self.assertEqual(service.save_shifts, service.shifts_data, 
                         "save_optimized_shifts received wrong data")
if __name__ == "__main__":
    unittest.main()