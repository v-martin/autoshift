from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from user.models import User
from user.serializers import AdminRoleApproveRequestSerializer, SignUpRequestSerializer, SignInRequestSerializer, \
    AuthResponseSerializer, UserResponseSerializer
from user.service import UserService

@extend_schema(
    tags=['user'],
)
class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpRequestSerializer
    permission_classes = [permissions.AllowAny]

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


