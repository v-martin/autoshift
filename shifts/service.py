from shifts.models import Shift


class ShiftService:
    def __init__(self, shift=None):
        self.shift = shift 