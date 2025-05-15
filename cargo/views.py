from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import CargoLoad, CargoForecast
from .serializers import CargoLoadSerializer, CargoForecastSerializer
from warehouses.models import Warehouse
from datetime import datetime, timedelta


@extend_schema_view(
    list=extend_schema(tags=['cargo']),
    retrieve=extend_schema(tags=['cargo']),
    create=extend_schema(tags=['cargo']),
    update=extend_schema(tags=['cargo']),
    partial_update=extend_schema(tags=['cargo']),
    destroy=extend_schema(tags=['cargo']),
    for_warehouse=extend_schema(tags=['cargo']),
    by_date_range=extend_schema(tags=['cargo']),
)
class CargoLoadViewSet(viewsets.ModelViewSet):
    queryset = CargoLoad.objects.all()
    serializer_class = CargoLoadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['warehouse', 'date']
    search_fields = ['warehouse__name']

    @extend_schema(
        parameters=[OpenApiParameter(name='warehouse_uuid', type=OpenApiTypes.STR)],
    )
    @action(detail=False, methods=['get'])
    def for_warehouse(self, request):
        warehouse_uuid = request.query_params.get('warehouse_uuid')
        if not warehouse_uuid:
            return Response({"error": "warehouse_uuid parameter is required"}, status=400)
        
        try:
            warehouse = Warehouse.objects.get(uuid=warehouse_uuid)
        except Warehouse.DoesNotExist:
            return Response({"error": "Warehouse not found"}, status=404)
        
        queryset = self.get_queryset().filter(warehouse=warehouse)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE),
        ],
    )
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        warehouse_uuid = request.query_params.get('warehouse_uuid')
        
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date parameters are required"}, status=400)
        
        queryset = self.get_queryset()
        
        if warehouse_uuid:
            try:
                warehouse = Warehouse.objects.get(uuid=warehouse_uuid)
                queryset = queryset.filter(warehouse=warehouse)
            except Warehouse.DoesNotExist:
                return Response({"error": "Warehouse not found"}, status=404)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=['cargo']),
    retrieve=extend_schema(tags=['cargo']),
    create=extend_schema(tags=['cargo']),
    update=extend_schema(tags=['cargo']),
    partial_update=extend_schema(tags=['cargo']),
    destroy=extend_schema(tags=['cargo']),
    future_week=extend_schema(tags=['cargo']),
)
class CargoForecastViewSet(viewsets.ModelViewSet):
    queryset = CargoForecast.objects.all()
    serializer_class = CargoForecastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['warehouse', 'date']
    search_fields = ['warehouse__name']

    @action(detail=False, methods=['get'])
    def future_week(self, request):
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        warehouse_uuid = request.query_params.get('warehouse_uuid')
        queryset = self.get_queryset().filter(date__gte=today, date__lte=next_week)
        
        if warehouse_uuid:
            try:
                warehouse = Warehouse.objects.get(uuid=warehouse_uuid)
                queryset = queryset.filter(warehouse=warehouse)
            except Warehouse.DoesNotExist:
                return Response({"error": "Warehouse not found"}, status=404)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
