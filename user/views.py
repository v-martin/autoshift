from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from user.models import User, WorkerQualification, WorkerWarehousePreference
from user.serializers import (
    AdminRoleApproveRequestSerializer, SignUpRequestSerializer, SignInRequestSerializer,
    AuthResponseSerializer, UserResponseSerializer, UpdateUserRequestSerializer,
    WorkerQualificationSerializer, WorkerQualificationCreateSerializer,
    WorkerWarehousePreferenceSerializer, WorkerWarehousePreferenceCreateSerializer
)
from user.service import UserService

@extend_schema(
    tags=['user'],
    description="Register a new user. The avatar field accepts image uploads.",
    methods=['POST'],
)
class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpRequestSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(AuthResponseSerializer({
            'message': 'User created successfully.',
            'user': user,
        }).data)


@extend_schema(
    tags=['user'],
)
class SignInView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignInRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if not user:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)

        return Response(AuthResponseSerializer({
            'message': 'Login successful.',
            'user': user,
        }).data)


@extend_schema(
    tags=['user'],
)
class AdminRoleApprovalView(GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminRoleApproveRequestSerializer
    queryset = User.objects.all()
    service = UserService

    @action(
        methods=['get'],
        detail=False,
        url_path='admin-approval-requests',
        url_name='admin-approval-requests',
    )
    def admin_approval_requests(self, request, *args, **kwargs):
        users = User.objects.filter(is_admin_requested=True, role='worker')
        serializer = UserResponseSerializer(users, many=True)
        return Response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        url_path='admin-approval',
        url_name='admin-approval',
    )
    def admin_approval(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.service(user=instance).approve_or_reject(serializer.validated_data['action'])

        return Response(status=status.HTTP_200_OK)

@extend_schema(
    tags=['user'],
)
class WorkersView(generics.ListAPIView):
    serializer_class = UserResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role=User.WORKER)

@extend_schema(
    tags=['user'],
    description="View and update user profile including avatar image.",
)
class UserProfileView(viewsets.GenericViewSet):
    serializer_class = UpdateUserRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        return self.request.user
    
    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserResponseSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(UserResponseSerializer(instance).data)
    
    @extend_schema(
        responses=WorkerQualificationSerializer(many=True),
        description="Get all qualifications of the current user"
    )
    @action(detail=False, methods=['get'], url_path='qualifications')
    def get_qualifications(self, request):
        qualifications = WorkerQualification.objects.filter(user=request.user)
        serializer = WorkerQualificationSerializer(qualifications, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=WorkerQualificationCreateSerializer,
        responses=WorkerQualificationSerializer,
        description="Add a new qualification for the current user"
    )
    @action(detail=False, methods=['post'], url_path='qualifications')
    def add_qualification(self, request):
        serializer = WorkerQualificationCreateSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        result_serializer = WorkerQualificationSerializer(serializer.instance)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        responses=WorkerWarehousePreferenceSerializer(many=True),
        description="Get all warehouse preferences of the current user"
    )
    @action(detail=False, methods=['get'], url_path='warehouse-preferences')
    def get_warehouse_preferences(self, request):
        preferences = WorkerWarehousePreference.objects.filter(user=request.user)
        serializer = WorkerWarehousePreferenceSerializer(preferences, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=WorkerWarehousePreferenceCreateSerializer,
        responses=WorkerWarehousePreferenceSerializer,
        description="Add a new warehouse preference for the current user"
    )
    @action(detail=False, methods=['post'], url_path='warehouse-preferences')
    def add_warehouse_preference(self, request):
        serializer = WorkerWarehousePreferenceCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        result_serializer = WorkerWarehousePreferenceSerializer(serializer.instance)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['user-qualifications'],
)
class WorkerQualificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkerQualificationCreateSerializer
        return WorkerQualificationSerializer
    
    def get_queryset(self):
        user_uuid = self.kwargs.get('user_uuid')
        if user_uuid:
            user = get_object_or_404(User, uuid=user_uuid)
            if self.request.user.role == User.ADMIN or self.request.user == user:
                return WorkerQualification.objects.filter(user=user)
            else:
                return WorkerQualification.objects.none()
        return WorkerQualification.objects.none()
    
    def perform_create(self, serializer):
        user_uuid = self.kwargs.get('user_uuid')
        user = get_object_or_404(User, uuid=user_uuid)
        
        if self.request.user.role == User.ADMIN or self.request.user == user:
            serializer.save(user=user)
        else:
            raise permissions.PermissionDenied("You don't have permission to add qualifications for this user")
    
    def perform_update(self, serializer):
        qualification = self.get_object()
        if self.request.user.role == User.ADMIN or self.request.user == qualification.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You don't have permission to update this qualification")

    def perform_destroy(self, instance):
        if self.request.user.role == User.ADMIN or self.request.user == instance.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You don't have permission to delete this qualification")
    
    @action(detail=False, methods=['get'], url_path='types')
    def qualification_types(self, request, user_uuid=None):
        types = [
            {'value': choice[0], 'display_name': choice[1]} 
            for choice in WorkerQualification.QUALIFICATION_CHOICES
        ]
        return Response(types)


@extend_schema(
    tags=['user-warehouse-preferences'],
)
class WorkerWarehousePreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkerWarehousePreferenceCreateSerializer
        return WorkerWarehousePreferenceSerializer
    
    def get_queryset(self):
        user_uuid = self.kwargs.get('user_uuid')
        if user_uuid:
            user = get_object_or_404(User, uuid=user_uuid)
            if self.request.user.role == User.ADMIN or self.request.user == user:
                return WorkerWarehousePreference.objects.filter(user=user)
            else:
                return WorkerWarehousePreference.objects.none()
        return WorkerWarehousePreference.objects.none()
    
    def perform_create(self, serializer):
        user_uuid = self.kwargs.get('user_uuid')
        user = get_object_or_404(User, uuid=user_uuid)
        
        if self.request.user.role == User.ADMIN or self.request.user == user:
            serializer.save(user=user)
        else:
            raise permissions.PermissionDenied("You don't have permission to add warehouse preferences for this user")
    
    def perform_update(self, serializer):
        preference = self.get_object()
        if self.request.user.role == User.ADMIN or self.request.user == preference.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You don't have permission to update this warehouse preference")

    def perform_destroy(self, instance):
        if self.request.user.role == User.ADMIN or self.request.user == instance.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You don't have permission to delete this warehouse preference")
    
    @action(detail=False, methods=['get'], url_path='available-warehouses')
    def available_warehouses(self, request, user_uuid=None):
        from warehouses.models import Warehouse
        from warehouses.serializers import WarehouseSerializer
        
        user = get_object_or_404(User, uuid=user_uuid) if user_uuid else request.user
        
        existing_warehouse_ids = WorkerWarehousePreference.objects.filter(
            user=user
        ).values_list('warehouse_id', flat=True)
        
        warehouses = Warehouse.objects.filter(is_active=True).exclude(
            id__in=existing_warehouse_ids
        )
        
        serializer = WarehouseSerializer(warehouses, many=True)
        return Response(serializer.data)
