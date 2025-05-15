from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CargoLoadViewSet, CargoForecastViewSet

router = DefaultRouter()
router.register(r'loads', CargoLoadViewSet)
router.register(r'forecasts', CargoForecastViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 