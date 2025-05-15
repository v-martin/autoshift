import logging
import datetime
from typing import List, Tuple
from django.conf import settings
from .client import ShiftOptimizerClient
logger = logging.getLogger(__name__)

class ShiftOptimizationService:
    def __init__(self):
        host = getattr(settings, 'SHIFT_OPTIMIZER_HOST', 'shift_optimizer')
        port = getattr(settings, 'SHIFT_OPTIMIZER_PORT', '50051')
        self.client = ShiftOptimizerClient(host=host, port=port)
    
    def optimize_shifts(self, start_date, end_date=None, warehouse_ids=None) -> Tuple[bool, str, List, List]:
        try:
            from user.models import User, WorkerQualification, WorkerWarehousePreference
            from warehouses.models import Warehouse
            from cargo.models import CargoLoad
            
            if not end_date:
                end_date = start_date
            
            if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date):
                return False, "Invalid date format", [], []
                
            if start_date > end_date:
                return False, "Start date cannot be after end date", [], []
            
            delta = end_date - start_date
            if delta.days > 14:
                return False, "Optimization period cannot exceed 14 days", [], []
            
            warehouse_queryset = Warehouse.objects.filter(is_active=True)
            if warehouse_ids:
                warehouse_queryset = warehouse_queryset.filter(id__in=warehouse_ids)
            
            warehouses = list(warehouse_queryset)
            
            if not warehouses:
                return False, "No active warehouses found", [], []
            
            workers = list(User.objects.filter(role='worker').prefetch_related(
                'qualifications', 'warehouse_preferences'
            ))
            
            if not workers:
                return False, "No active workers found", [], []
            
            cargo_loads = list(CargoLoad.objects.filter(
                date__gte=start_date,
                date__lte=end_date,
                warehouse__in=warehouses
            ))
            
            days = []
            current_date = start_date
            while current_date <= end_date:
                days.append(current_date.strftime("%A").lower())
                current_date += datetime.timedelta(days=1)
            
            try:
                logger.info(f"Calling optimization service with {len(workers)} workers, {len(warehouses)} warehouses, {len(cargo_loads)} cargo loads")
                success, message, shifts, staffing = self.client.optimize_shifts(workers, warehouses, cargo_loads, days)
            except Exception as e:
                logger.error(f"Error communicating with optimizer service: {str(e)}", exc_info=True)
                return False, f"Error: {str(e)}", [], []
            
            if not success:
                logger.error(f"Optimization failed: {message}")
                return success, message, shifts, staffing
            
            logger.info(f"Optimization successful. Received {len(shifts)} shifts")
            
            save_success, save_message, saved_count = self.save_optimized_shifts(shifts)
            
            if not save_success:
                logger.warning(f"Failed to save shifts: {save_message}")
            else:
                logger.info(f"Saved {saved_count} shifts successfully")
            
            return success, message, shifts, staffing
        except Exception as e:
            logger.error(f"Error in shift optimization service: {str(e)}", exc_info=True)
            return False, f"Error: {str(e)}", [], []
    
    def save_optimized_shifts(self, shifts) -> Tuple[bool, str, int]:
        try:
            from user.models import User
            from warehouses.models import Warehouse
            from shifts.models import Shift
            
            saved_count = 0
            
            for shift_data in shifts:
                try:
                    user = User.objects.get(uuid=shift_data['worker_uuid'])
                    warehouse = Warehouse.objects.get(uuid=shift_data['warehouse_uuid'])
                    
                    shift, created = Shift.objects.update_or_create(
                        user=user,
                        warehouse=warehouse,
                        day_of_week=shift_data['day_of_week'],
                        defaults={
                            'start_time': shift_data['start_time'],
                            'end_time': shift_data['end_time'],
                            'is_optimized': True
                        }
                    )
                    
                    saved_count += 1
                    
                except User.DoesNotExist:
                    logger.warning(f"User with UUID {shift_data['worker_uuid']} not found")
                    continue
                except Warehouse.DoesNotExist:
                    logger.warning(f"Warehouse with UUID {shift_data['warehouse_uuid']} not found")
                    continue
                except Exception as e:
                    logger.error(f"Error saving shift: {str(e)}", exc_info=True)
                    continue
            
            return True, f"Successfully saved {saved_count} shifts", saved_count
            
        except Exception as e:
            logger.error(f"Error saving optimized shifts: {str(e)}", exc_info=True)
            return False, f"Error: {str(e)}", 0