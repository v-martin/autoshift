from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from autoshift.permissions import IsAdminUser
from warehouses.models import Warehouse
from warehouses.serializers import (
    WarehouseSerializer, 
    WarehouseCreateSerializer, 
    WarehouseUpdateSerializer, 
    WarehouseResponseSerializer,
)
from warehouses.service import WarehouseService


@extend_schema(
    tags=['warehouses'],
)
class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    lookup_field = 'uuid'
    service = WarehouseService

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return WarehouseCreateSerializer
        if self.action in ['update', 'partial_update']:
            return WarehouseUpdateSerializer
        return WarehouseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.save()
        
        return Response(
            WarehouseResponseSerializer(warehouse).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.save()

        return Response(
            WarehouseResponseSerializer(warehouse).data,
            status=status.HTTP_200_OK,
        )
