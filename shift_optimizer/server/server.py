import logging
import grpc
import time
from concurrent import futures
from typing import List
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import shift_optimizer.shift_optimizer_pb2 as shift_optimizer_pb2
import shift_optimizer.shift_optimizer_pb2_grpc as shift_optimizer_pb2_grpc
from .optimizer import ShiftOptimizer
from .models import Worker, Warehouse, CargoLoad, Qualification, WarehousePreference
logger = logging.getLogger(__name__)
class ShiftOptimizerServicer(shift_optimizer_pb2_grpc.ShiftOptimizerServiceServicer):
    def OptimizeShifts(self, request, context):
        logger.info("Received optimization request")
        
        try:
            workers = self._convert_workers(request.workers)
            warehouses = self._convert_warehouses(request.warehouses)
            cargo_loads = self._convert_cargo_loads(request.cargo_loads)
            days = list(request.days)
            
            optimizer = ShiftOptimizer(workers, warehouses, cargo_loads, days)
            shifts, warehouse_staffing = optimizer.optimize()
            
            response = shift_optimizer_pb2.OptimizeShiftsResponse()
            response.success = True
            
            for shift in shifts:
                grpc_shift = response.shifts.add()
                grpc_shift.worker_uuid = shift.worker_uuid
                grpc_shift.warehouse_uuid = shift.warehouse_uuid
                grpc_shift.day_of_week = shift.day_of_week
                grpc_shift.start_time = shift.start_time
                grpc_shift.end_time = shift.end_time
            
            for staffing in warehouse_staffing:
                grpc_staffing = response.warehouse_staffing.add()
                grpc_staffing.warehouse_uuid = staffing.warehouse_uuid
                grpc_staffing.warehouse_name = staffing.warehouse_name
                grpc_staffing.day = staffing.day
                grpc_staffing.required_basic_workers = staffing.required_basic_workers
                grpc_staffing.scheduled_basic_workers = staffing.scheduled_basic_workers
                grpc_staffing.required_drivers = staffing.required_drivers
                grpc_staffing.scheduled_drivers = staffing.scheduled_drivers
                grpc_staffing.required_engineers = staffing.required_engineers
                grpc_staffing.scheduled_engineers = staffing.scheduled_engineers
                grpc_staffing.is_fully_staffed = staffing.is_fully_staffed
            
            logger.info(f"Optimization completed. Returning {len(shifts)} shifts")
            return response
            
        except Exception as e:
            logger.error(f"Error during optimization: {str(e)}", exc_info=True)
            response = shift_optimizer_pb2.OptimizeShiftsResponse()
            response.success = False
            response.message = f"Error: {str(e)}"
            return response
    
    def _convert_workers(self, grpc_workers) -> List[Worker]:
        workers = []
        
        for grpc_worker in grpc_workers:
            qualifications = []
            for grpc_qual in grpc_worker.qualifications:
                qual_type = shift_optimizer_pb2.QualificationType.Name(grpc_qual.type)
                qualifications.append(Qualification(
                    type=qual_type,
                    level=grpc_qual.level
                ))
            
            preferences = []
            for grpc_pref in grpc_worker.warehouse_preferences:
                preferences.append(WarehousePreference(
                    warehouse_uuid=grpc_pref.warehouse_uuid,
                    priority=grpc_pref.priority,
                    distance=grpc_pref.distance
                ))
            
            worker = Worker(
                uuid=grpc_worker.uuid,
                username=grpc_worker.username,
                qualifications=qualifications,
                warehouse_preferences=preferences
            )
            workers.append(worker)
        
        return workers
    
    def _convert_warehouses(self, grpc_warehouses) -> List[Warehouse]:
        warehouses = []
        
        for grpc_warehouse in grpc_warehouses:
            warehouse = Warehouse(
                uuid=grpc_warehouse.uuid,
                name=grpc_warehouse.name,
                capacity=grpc_warehouse.capacity,
                min_workers=grpc_warehouse.min_workers,
                min_basic_workers=grpc_warehouse.min_basic_workers,
                min_drivers=grpc_warehouse.min_drivers,
                min_engineers=grpc_warehouse.min_engineers,
                is_active=grpc_warehouse.is_active
            )
            warehouses.append(warehouse)
        
        return warehouses
    
    def _convert_cargo_loads(self, grpc_cargo_loads) -> List[CargoLoad]:
        cargo_loads = []
        
        for grpc_cargo in grpc_cargo_loads:
            cargo = CargoLoad(
                warehouse_uuid=grpc_cargo.warehouse_uuid,
                date=grpc_cargo.date,
                total_weight=grpc_cargo.total_weight
            )
            cargo_loads.append(cargo)
        
        return cargo_loads
def serve(port='50051'):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    shift_optimizer_pb2_grpc.add_ShiftOptimizerServiceServicer_to_server(
        ShiftOptimizerServicer(), server
    )
    
    server_address = f'[::]:{port}'
    server.add_insecure_port(server_address)
    server.start()
    
    logger.info(f"Shift Optimizer gRPC server started and listening on {server_address}")
    logger.info(f"Server is ready to receive requests")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        logger.info("Server stopped")
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()