#!/usr/bin/env python
import argparse
import datetime
import logging
import os

from shift_optimizer.client.client import ShiftOptimizerClient
from shift_optimizer.server.models import Worker, Warehouse, CargoLoad, Qualification, WarehousePreference

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_optimization(host, port):
    """
    Запускает тестовую оптимизацию с использованием демонстрационных данных.
    """
    logger.info(f"Testing optimization with host={host}, port={port}")
    
    # Создаем тестового клиента
    client = ShiftOptimizerClient(host=host, port=port)
    
    # Создаем тестовые данные
    
    # Работники
    workers = []
    for i in range(1, 6):
        qualifications = []
        if i % 3 == 0:
            qualifications.append(Qualification(type="BASIC_WORKER", level=2))
        elif i % 3 == 1:
            qualifications.append(Qualification(type="CARGO_DRIVER", level=3))
        else:
            qualifications.append(Qualification(type="ENGINEER", level=2))
        
        preferences = []
        preferences.append(WarehousePreference(warehouse_uuid=f"w-{i % 2 + 1}", priority=1, distance=5.0))
        
        worker = Worker(
            uuid=f"worker-{i}",
            username=f"Worker {i}",
            qualifications=qualifications,
            warehouse_preferences=preferences
        )
        workers.append(worker)
    
    # Склады
    warehouses = []
    for i in range(1, 3):
        warehouse = Warehouse(
            uuid=f"w-{i}",
            name=f"Warehouse {i}",
            capacity=10,
            min_workers=2,
            min_basic_workers=1,
            min_drivers=1,
            min_engineers=0,
            is_active=True
        )
        warehouses.append(warehouse)
    
    # Грузы
    cargo_loads = []
    today = datetime.date.today()
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        cargo = CargoLoad(
            warehouse_uuid=f"w-{i % 2 + 1}",
            date=date.strftime("%Y-%m-%d"),
            total_weight=1000 * (i + 1)
        )
        cargo_loads.append(cargo)
    
    # Дни недели
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    
    # Запускаем оптимизацию
    logger.info("Starting test optimization...")
    success, message, shifts, staffing = client.optimize_shifts(workers, warehouses, cargo_loads, days)
    
    if success:
        logger.info(f"Optimization successful: {message}")
        logger.info(f"Generated {len(shifts)} shifts")
        for i, shift in enumerate(shifts[:5]):  # Показываем первые 5 смен
            logger.info(f"Shift {i+1}: Worker {shift['worker_uuid']} at Warehouse {shift['warehouse_uuid']} on {shift['day_of_week']}")
        
        logger.info(f"Staffing information for {len(staffing)} warehouse-days")
        for i, staff in enumerate(staffing[:3]):  # Показываем первые 3 отчета о укомплектованности
            logger.info(f"Staffing {i+1}: Warehouse {staff['warehouse_name']} on {staff['day']}, fully staffed: {staff['is_fully_staffed']}")
    else:
        logger.error(f"Optimization failed: {message}")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Shift Optimizer')
    parser.add_argument('--host', default='shift_optimizer', help='Host address of optimizer server')
    parser.add_argument('--port', default='50051', help='Port number of optimizer server')
    
    args = parser.parse_args()
    test_optimization(args.host, args.port) 