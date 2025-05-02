from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from user.views import SignUpView, SignInView, AdminRoleApprovalView, WorkersView, UserProfileView


router = DefaultRouter(trailing_slash=True)

router.register(f'user', AdminRoleApprovalView)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('workers/', WorkersView.as_view(), name='workers'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]

urlpatterns += router.urls
