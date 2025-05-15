import grpc
import logging
import sys
import os
from typing import List, Tuple
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import shift_optimizer.shift_optimizer_pb2 as shift_optimizer_pb2
import shift_optimizer.shift_optimizer_pb2_grpc as shift_optimizer_pb2_grpc
logger = logging.getLogger(__name__)

class ShiftOptimizerClient:
    def __init__(self, host='shift_optimizer', port='50051'):
        logger.info(f"Initializing ShiftOptimizerClient with host={host}, port={port}")
        try:
            self.channel = grpc.insecure_channel(f'{host}:{port}')
            self.stub = shift_optimizer_pb2_grpc.ShiftOptimizerServiceStub(self.channel)
            logger.info(f"Successfully connected to gRPC server at {host}:{port}")
        except Exception as e:
            logger.error(f"Error initializing gRPC client: {str(e)}")
            raise
    
    def optimize_shifts(self, workers, warehouses, cargo_loads, days) -> Tuple[bool, str, List, List]:
        try:
            logger.info(f"Creating optimization request with {len(workers)} workers, {len(warehouses)} warehouses")
            request = shift_optimizer_pb2.OptimizeShiftsRequest()
            
            for worker in workers:
                grpc_worker = request.workers.add()
                grpc_worker.uuid = str(worker.uuid)
                grpc_worker.username = worker.username
                
                qual_count = 0
                for qualification in worker.qualifications.all():
                    grpc_qual = grpc_worker.qualifications.add()
                    
                    if qualification.qualification_type == 'basic_worker':
                        grpc_qual.type = shift_optimizer_pb2.QualificationType.BASIC_WORKER
                    elif qualification.qualification_type == 'cargo_driver':
                        grpc_qual.type = shift_optimizer_pb2.QualificationType.CARGO_DRIVER
                    elif qualification.qualification_type == 'engineer':
                        grpc_qual.type = shift_optimizer_pb2.QualificationType.ENGINEER
                    
                    grpc_qual.level = qualification.level
                    qual_count += 1
                
                pref_count = 0
                for preference in worker.warehouse_preferences.all():
                    grpc_pref = grpc_worker.warehouse_preferences.add()
                    grpc_pref.warehouse_uuid = str(preference.warehouse.uuid)
                    grpc_pref.priority = preference.priority
                    grpc_pref.distance = float(preference.distance or 0)
                    pref_count += 1
                
                logger.debug(f"Added worker {worker.username} with {qual_count} qualifications and {pref_count} preferences")
            
            for warehouse in warehouses:
                grpc_warehouse = request.warehouses.add()
                grpc_warehouse.uuid = str(warehouse.uuid)
                grpc_warehouse.name = warehouse.name
                grpc_warehouse.capacity = warehouse.capacity
                grpc_warehouse.min_workers = warehouse.min_workers
                grpc_warehouse.min_basic_workers = warehouse.min_basic_workers
                grpc_warehouse.min_drivers = warehouse.min_drivers
                grpc_warehouse.min_engineers = warehouse.min_engineers
                grpc_warehouse.is_active = warehouse.is_active
                logger.debug(f"Added warehouse {warehouse.name}")
            
            for cargo in cargo_loads:
                grpc_cargo = request.cargo_loads.add()
                grpc_cargo.warehouse_uuid = str(cargo.warehouse.uuid)
                grpc_cargo.date = cargo.date.strftime("%Y-%m-%d")
                grpc_cargo.total_weight = cargo.total_weight
                logger.debug(f"Added cargo load for {cargo.date} at warehouse {cargo.warehouse.name}")
            
            for day in days:
                request.days.append(day)
            
            logger.info(f"Sending optimization request for days: {days}")
            
            # Установка таймаута для вызова gRPC
            response = self.stub.OptimizeShifts(
                request,
                timeout=30.0  # 30 секунд таймаут
            )
            
            if response.success:
                shifts = []
                for shift in response.shifts:
                    shifts.append({
                        'worker_uuid': shift.worker_uuid,
                        'warehouse_uuid': shift.warehouse_uuid,
                        'day_of_week': shift.day_of_week,
                        'start_time': shift.start_time,
                        'end_time': shift.end_time
                    })
                
                staffing = []
                for staff_info in response.warehouse_staffing:
                    staffing.append({
                        'warehouse_uuid': staff_info.warehouse_uuid,
                        'warehouse_name': staff_info.warehouse_name,
                        'day': staff_info.day,
                        'required_basic_workers': staff_info.required_basic_workers,
                        'scheduled_basic_workers': staff_info.scheduled_basic_workers,
                        'required_drivers': staff_info.required_drivers,
                        'scheduled_drivers': staff_info.scheduled_drivers,
                        'required_engineers': staff_info.required_engineers,
                        'scheduled_engineers': staff_info.scheduled_engineers,
                        'is_fully_staffed': staff_info.is_fully_staffed
                    })
                
                logger.info(f"Optimization successful. Received {len(shifts)} shifts")
                return True, "Optimization successful", shifts, staffing
            else:
                logger.error(f"Optimization failed: {response.message}")
                return False, response.message, [], []
                
        except grpc.RpcError as e:
            status_code = e.code()
            if status_code == grpc.StatusCode.UNAVAILABLE:
                error_msg = f"Cannot connect to the optimizer server: {str(e)}. Please check that the server is running."
            elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                error_msg = "Request to optimizer server timed out."
            else:
                error_msg = f"gRPC error: {str(e)}"
            
            logger.error(f"gRPC error: {error_msg}", exc_info=True)
            return False, error_msg, [], []
        except Exception as e:
            error_msg = f"Error during optimization: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, [], []