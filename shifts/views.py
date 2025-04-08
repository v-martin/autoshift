from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from autoshift.permissions import IsAdminOrIsOwner
from shifts.models import Shift
from shifts.serializers import ShiftSerializer, ShiftCreateSerializer, ShiftUpdateSerializer, ShiftResponseSerializer
from shifts.service import ShiftService


@extend_schema(
    tags=['shifts'],
)
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrIsOwner]
    lookup_field = 'uuid'
    service = ShiftService
    
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