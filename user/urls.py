from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from user.views import (
    SignUpView, SignInView, AdminRoleApprovalView, WorkersView, UserProfileView,
    WorkerQualificationViewSet, WorkerWarehousePreferenceViewSet
)


router = DefaultRouter(trailing_slash=False)

router.register(r'user', AdminRoleApprovalView)
router.register(r'users/(?P<user_uuid>[\w-]+)/qualifications', WorkerQualificationViewSet, basename='user-qualifications')
router.register(r'users/(?P<user_uuid>[\w-]+)/warehouse-preferences', WorkerWarehousePreferenceViewSet, basename='user-warehouse-preferences')
router.register(r'profile', UserProfileView, basename='profile')

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('workers/', WorkersView.as_view(), name='workers'),
]

urlpatterns += router.urls
