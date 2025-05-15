import logging
from datetime import datetime, time
from typing import Dict, List, Tuple, Set
from .models import Worker, Warehouse, CargoLoad, ScheduledShift, WarehouseStaffing, Qualification
logger = logging.getLogger(__name__)
class ShiftOptimizer:
    def __init__(self, workers: List[Worker], warehouses: List[Warehouse], 
                 cargo_loads: List[CargoLoad], days: List[str]):
        self.workers = workers
        self.warehouses = {w.uuid: w for w in warehouses}
        self.cargo_loads = cargo_loads
        self.days = days
        
        self.shift_times = [
            (time(8, 0), time(16, 0)),
            (time(16, 0), time(0, 0)),
        ]
        
        self.scheduled_workers = {day: set() for day in days}
        
        self.shifts = []
        self.warehouse_staffing = []
    
    def optimize(self) -> Tuple[List[ScheduledShift], List[WarehouseStaffing]]:
        logger.info("Starting shift optimization")
        
        self.shifts = []
        self.warehouse_staffing = []
        self.scheduled_workers = {day: set() for day in self.days}
        
        warehouse_requirements = self._calculate_warehouse_requirements()
        
        self._assign_minimum_staff(warehouse_requirements)
        
        self._assign_additional_staff(warehouse_requirements)
        
        self._generate_staffing_reports(warehouse_requirements)
        
        logger.info(f"Optimization completed. Scheduled {len(self.shifts)} shifts")
        
        return self.shifts, self.warehouse_staffing
    
    def _calculate_warehouse_requirements(self) -> Dict:
        requirements = {}
        
        for day in self.days:
            requirements[day] = {}
            
            for warehouse_uuid, warehouse in self.warehouses.items():
                req = {
                    'warehouse_uuid': warehouse_uuid,
                    'warehouse_name': warehouse.name,
                    'min_basic_workers': warehouse.min_basic_workers,
                    'min_drivers': warehouse.min_drivers,
                    'min_engineers': warehouse.min_engineers,
                    'total_basic_workers': warehouse.min_basic_workers,
                    'total_drivers': warehouse.min_drivers,
                    'total_engineers': warehouse.min_engineers,
                    'scheduled_basic_workers': 0,
                    'scheduled_drivers': 0,
                    'scheduled_engineers': 0
                }
                
                cargo_for_day = [c for c in self.cargo_loads
                                if c.warehouse_uuid == warehouse_uuid and self._map_date_to_day(c.date) == day]
                
                for cargo in cargo_for_day:
                    basic_workers = max(warehouse.min_basic_workers, 
                                        (cargo.total_weight // 1000) + (1 if cargo.total_weight % 1000 > 0 else 0))
                    
                    drivers = max(warehouse.min_drivers,
                                 (cargo.total_weight // 5000) + (1 if cargo.total_weight % 5000 > 0 else 0))
                    
                    engineers = max(warehouse.min_engineers,
                                   (cargo.total_weight // 10000) + (1 if cargo.total_weight % 10000 > 0 else 0))
                    
                    req['total_basic_workers'] = max(req['total_basic_workers'], basic_workers)
                    req['total_drivers'] = max(req['total_drivers'], drivers)
                    req['total_engineers'] = max(req['total_engineers'], engineers)
                
                requirements[day][warehouse_uuid] = req
        
        return requirements
    
    def _assign_minimum_staff(self, warehouse_requirements: Dict):
        logger.info("Assigning minimum staff requirements")
        
        for day in self.days:
            for warehouse_uuid, req in warehouse_requirements[day].items():
                sorted_workers = self._sort_workers_by_preference(warehouse_uuid)
                
                self._assign_workers_by_qualification(
                    sorted_workers, 
                    day, 
                    warehouse_uuid,
                    "BASIC_WORKER", 
                    req['min_basic_workers'],
                    req
                )
                
                self._assign_workers_by_qualification(
                    sorted_workers, 
                    day, 
                    warehouse_uuid,
                    "CARGO_DRIVER", 
                    req['min_drivers'],
                    req
                )
                
                self._assign_workers_by_qualification(
                    sorted_workers, 
                    day, 
                    warehouse_uuid,
                    "ENGINEER", 
                    req['min_engineers'],
                    req
                )
    
    def _assign_additional_staff(self, warehouse_requirements: Dict):
        logger.info("Assigning additional staff based on cargo requirements")
        
        for day in self.days:
            for warehouse_uuid, req in warehouse_requirements[day].items():
                sorted_workers = self._sort_workers_by_preference(warehouse_uuid)
                
                additional_basic = req['total_basic_workers'] - req['scheduled_basic_workers']
                if additional_basic > 0:
                    self._assign_workers_by_qualification(
                        sorted_workers, 
                        day, 
                        warehouse_uuid,
                        "BASIC_WORKER", 
                        additional_basic,
                        req
                    )
                
                additional_drivers = req['total_drivers'] - req['scheduled_drivers']
                if additional_drivers > 0:
                    self._assign_workers_by_qualification(
                        sorted_workers, 
                        day, 
                        warehouse_uuid,
                        "CARGO_DRIVER", 
                        additional_drivers,
                        req
                    )
                
                additional_engineers = req['total_engineers'] - req['scheduled_engineers']
                if additional_engineers > 0:
                    self._assign_workers_by_qualification(
                        sorted_workers, 
                        day, 
                        warehouse_uuid,
                        "ENGINEER", 
                        additional_engineers,
                        req
                    )
    
    def _sort_workers_by_preference(self, warehouse_uuid: str) -> List[Worker]:
        result = []
        logger.info(self.workers)
        
        for worker in self.workers:
            logger.info(worker.warehouse_preferences)
            preference = None
            for p in worker.warehouse_preferences:
                if p.warehouse_uuid == warehouse_uuid:
                    preference = p
                    break
            
            if preference:
                result.append((worker, preference.priority, preference.distance))
            else:
                result.append((worker, 9999, 9999))
        
        result.sort(key=lambda x: (x[1], x[2]))
        
        return [item[0] for item in result]
    
    def _assign_workers_by_qualification(self, workers: List[Worker], day: str, 
                                        warehouse_uuid: str, qualification_type: str, 
                                        required_count: int, req: Dict):
        if required_count <= 0:
            return
        
        assigned_count = 0
        
        for worker in workers:
            if worker.uuid in self.scheduled_workers[day]:
                continue
            
            has_qualification = any(q.type == qualification_type for q in worker.qualifications)
            
            if not has_qualification:
                continue
            shift_time = self.shift_times[0]
            
            shift = ScheduledShift(
                worker_uuid=worker.uuid,
                warehouse_uuid=warehouse_uuid,
                day_of_week=day,
                start_time=shift_time[0].strftime("%H:%M"),
                end_time=shift_time[1].strftime("%H:%M") if shift_time[1] != time(0, 0) else "00:00"
            )
            
            self.shifts.append(shift)
            self.scheduled_workers[day].add(worker.uuid)
            
            if qualification_type == "BASIC_WORKER":
                req['scheduled_basic_workers'] += 1
            elif qualification_type == "CARGO_DRIVER":
                req['scheduled_drivers'] += 1
            elif qualification_type == "ENGINEER":
                req['scheduled_engineers'] += 1
            
            assigned_count += 1
            if assigned_count >= required_count:
                break
    
    def _generate_staffing_reports(self, warehouse_requirements: Dict):
        for day in self.days:
            for warehouse_uuid, req in warehouse_requirements[day].items():
                staffing = WarehouseStaffing(
                    warehouse_uuid=warehouse_uuid,
                    warehouse_name=req['warehouse_name'],
                    day=day,
                    required_basic_workers=req['total_basic_workers'],
                    scheduled_basic_workers=req['scheduled_basic_workers'],
                    required_drivers=req['total_drivers'],
                    scheduled_drivers=req['scheduled_drivers'],
                    required_engineers=req['total_engineers'],
                    scheduled_engineers=req['scheduled_engineers'],
                    is_fully_staffed=(req['scheduled_basic_workers'] >= req['total_basic_workers'] and
                                    req['scheduled_drivers'] >= req['total_drivers'] and
                                    req['scheduled_engineers'] >= req['total_engineers'])
                )
                
                self.warehouse_staffing.append(staffing)
    
    def _map_date_to_day(self, date_str: str) -> str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%A").lower()