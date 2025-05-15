from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
@dataclass
class Qualification:
    type: str
    level: int
@dataclass
class WarehousePreference:
    warehouse_uuid: str
    priority: int
    distance: float
@dataclass
class Worker:
    uuid: str
    username: str
    qualifications: List[Qualification] = field(default_factory=list)
    warehouse_preferences: List[dict] = field(default_factory=list)
@dataclass
class Warehouse:
    uuid: str
    name: str
    capacity: int
    min_workers: int
    min_basic_workers: int
    min_drivers: int
    min_engineers: int
    is_active: bool
@dataclass
class CargoLoad:
    warehouse_uuid: str
    date: str
    total_weight: int
@dataclass
class ScheduledShift:
    worker_uuid: str
    warehouse_uuid: str
    day_of_week: str
    start_time: str
    end_time: str
@dataclass
class WarehouseStaffing:
    warehouse_uuid: str
    warehouse_name: str
    day: str
    required_basic_workers: int
    scheduled_basic_workers: int
    required_drivers: int
    scheduled_drivers: int
    required_engineers: int
    scheduled_engineers: int
    is_fully_staffed: bool 