from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.views.generic import TemplateView
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse

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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'shifts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get shifts based on user role
        if user.role == 'admin':
            shifts = Shift.objects.all()
        else:
            shifts = Shift.objects.filter(user=user)
            
        context['shifts'] = shifts.select_related('user', 'warehouse')
        return context


class TestApiView(TemplateView):
    template_name = 'shifts/test_api.html'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def shift_statistics(request):
    """Get statistics for shifts to populate dashboard charts"""
    user = request.user
    
    # Get relevant shifts based on user role
    if user.role == 'admin':
        shifts = Shift.objects.all()
    else:
        shifts = Shift.objects.filter(user=user)
        
    # Get shifts by day of week
    shifts_by_day = shifts.values('day_of_week').annotate(count=Count('id'))
    shifts_by_day_dict = {item['day_of_week']: item['count'] for item in shifts_by_day}
    
    # Get staff distribution by warehouse
    staff_by_warehouse = shifts.values('warehouse__name').annotate(count=Count('user', distinct=True))
    staff_by_warehouse_dict = {item['warehouse__name']: item['count'] for item in staff_by_warehouse}
    
    return Response({
        'shifts_by_day': shifts_by_day_dict,
        'staff_by_warehouse': staff_by_warehouse_dict,
    })


def stats_json(request):
    """A plain Django view that returns statistics as JSON (no authentication required for testing)"""
    # Get all shifts
    shifts = Shift.objects.all()
        
    # Get shifts by day of week
    shifts_by_day = shifts.values('day_of_week').annotate(count=Count('id'))
    shifts_by_day_dict = {item['day_of_week']: item['count'] for item in shifts_by_day}
    
    # Get staff distribution by warehouse
    staff_by_warehouse = shifts.values('warehouse__name').annotate(count=Count('user', distinct=True))
    staff_by_warehouse_dict = {item['warehouse__name']: item['count'] for item in staff_by_warehouse}
    
    return JsonResponse({
        'shifts_by_day': shifts_by_day_dict,
        'staff_by_warehouse': staff_by_warehouse_dict,
    })


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
        
    @action(
        detail=False,
        methods=['get'],
        url_path='statistics',
    )
    def statistics(self, request):
        """Get statistics for shifts to populate dashboard charts"""
        user = request.user
        
        # Get relevant shifts based on user role
        if user.role == 'admin':
            shifts = Shift.objects.all()
        else:
            shifts = Shift.objects.filter(user=user)
            
        # Get shifts by day of week
        shifts_by_day = shifts.values('day_of_week').annotate(count=Count('id'))
        shifts_by_day_dict = {item['day_of_week']: item['count'] for item in shifts_by_day}
        
        # Get staff distribution by warehouse
        staff_by_warehouse = shifts.values('warehouse__name').annotate(count=Count('user', distinct=True))
        staff_by_warehouse_dict = {item['warehouse__name']: item['count'] for item in staff_by_warehouse}
        
        return Response({
            'shifts_by_day': shifts_by_day_dict,
            'staff_by_warehouse': staff_by_warehouse_dict,
        })
