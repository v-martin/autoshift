from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from autoshift.permissions import IsAdminOrIsOwner
from shifts.models import Shift
from shifts.serializers import (
    ShiftSerializer, 
    ShiftCreateSerializer, 
    ShiftUpdateSerializer, 
    ShiftResponseSerializer,
    ShiftOptimizationRequestSerializer,
    ShiftOptimizationResponseSerializer
)
from shifts.service import ShiftService


@extend_schema(
    tags=['shifts'],
)
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrIsOwner]
    lookup_field = 'uuid'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Shift.objects.all()
        return Shift.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ShiftCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ShiftUpdateSerializer
        if self.action == 'optimize':
            return ShiftOptimizationRequestSerializer
        return ShiftSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift = serializer.save()
        
        return Response(
            ShiftResponseSerializer(shift).data,
            status=status.HTTP_201_CREATED,
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        shift = serializer.save()
        
        return Response(
            ShiftResponseSerializer(shift).data,
            status=status.HTTP_200_OK,
        )
        
    @extend_schema(
        request=ShiftOptimizationRequestSerializer,
        responses={200: ShiftOptimizationResponseSerializer},
        description="Optimize shifts for a specific date range and warehouses",
    )
    @action(
        detail=False, 
        methods=['post'], 
        url_path='optimize',
    )
    def optimize(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data.get('end_date', start_date)
        warehouse_ids = serializer.validated_data.get('warehouse_ids')
        
        service = ShiftService()
        result = service.optimize_shifts(
            start_date=start_date,
            end_date=end_date,
            warehouse_ids=warehouse_ids
        )
        
        response_serializer = ShiftOptimizationResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
