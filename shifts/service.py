import logging
from typing import Dict, List, Tuple
from shift_optimizer.client.django_integration import ShiftOptimizationService

logger = logging.getLogger(__name__)

class ShiftService:
    def __init__(self):
        self.optimizer = ShiftOptimizationService()
    
    def optimize_shifts(self, start_date, end_date=None, warehouse_ids=None) -> Dict:
        """
        Оптимизирует смены для заданного диапазона дат и складов.
        
        Args:
            start_date: Начальная дата оптимизации
            end_date: Конечная дата оптимизации (по умолчанию равна start_date)
            warehouse_ids: Список ID складов для оптимизации (опционально)
            
        Returns:
            Dict: Словарь с результатами оптимизации:
                {
                    'success': bool,
                    'message': str,
                    'shifts': List[Dict],
                    'warehouse_staffing': List[Dict]
                }
        """
        logger.info(f"Starting shift optimization for date range {start_date} to {end_date}")
        
        success, message, shifts, staffing = self.optimizer.optimize_shifts(
            start_date=start_date,
            end_date=end_date,
            warehouse_ids=warehouse_ids
        )
        
        return {
            'success': success,
            'message': message,
            'shifts': shifts,
            'warehouse_staffing': staffing
        }
