import pytest
from datetime import date

from warehouses.models import Warehouse
from cargo.models import CargoLoad, CargoForecast


class TestCargoLoadModel:
    def test_cargo_load_creation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50,
            min_workers=3,
            min_basic_workers=1,
            min_drivers=1,
            min_engineers=1
        )
        
        cargo_load = CargoLoad.objects.create(
            warehouse=warehouse,
            date=date.today(),
            total_weight=5000
        )
        
        assert isinstance(cargo_load, CargoLoad)
        assert cargo_load.warehouse == warehouse
        assert cargo_load.date == date.today()
        assert cargo_load.total_weight == 5000
        assert str(cargo_load) == f"{warehouse.name} - {date.today()} - 5000kg"
        
    def test_cargo_load_str_representation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        cargo_load = CargoLoad.objects.create(
            warehouse=warehouse,
            date=date.today(),
            total_weight=7500
        )
        
        expected_str = f"{warehouse.name} - {date.today()} - 7500kg"
        assert str(cargo_load) == expected_str


class TestCargoForecastModel:
    def test_cargo_forecast_creation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        forecast_date = date.today()
        
        cargo_forecast = CargoForecast.objects.create(
            warehouse=warehouse,
            date=forecast_date,
            predicted_weight=6000,
            confidence=0.85
        )
        
        assert isinstance(cargo_forecast, CargoForecast)
        assert cargo_forecast.warehouse == warehouse
        assert cargo_forecast.date == forecast_date
        assert cargo_forecast.predicted_weight == 6000
        assert cargo_forecast.confidence == 0.85
        assert str(cargo_forecast) == f"{warehouse.name} - {forecast_date} - 6000kg (85% confidence)"
        
    def test_cargo_forecast_str_representation(self, db):
        warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            address="123 Test St",
            capacity=50
        )
        
        forecast_date = date.today()
        
        cargo_forecast = CargoForecast.objects.create(
            warehouse=warehouse,
            date=forecast_date,
            predicted_weight=8000,
            confidence=0.75
        )
        
        expected_str = f"{warehouse.name} - {forecast_date} - 8000kg (75% confidence)"
        assert str(cargo_forecast) == expected_str 