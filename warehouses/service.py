from warehouses.models import Warehouse


class WarehouseService:
    def __init__(self, warehouse=None):
        self.warehouse = warehouse 