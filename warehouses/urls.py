from django.urls import path
from rest_framework.routers import DefaultRouter

from warehouses.views import WarehouseViewSet


router = DefaultRouter(trailing_slash=True)
router.register(r'warehouses', WarehouseViewSet)

urlpatterns = []

urlpatterns += router.urls 