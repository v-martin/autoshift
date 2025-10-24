from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shifts.views import ShiftViewSet, DashboardView, shift_statistics, TestApiView, stats_json

router = DefaultRouter()
router.register('shifts', ShiftViewSet, basename='shift')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='shifts_dashboard'),
    path('test-api/', TestApiView.as_view(), name='test_api'),
    path('api/statistics/', shift_statistics, name='shift_statistics'),
    path('api/stats.json', stats_json, name='stats_json'),
    path('api/', include(router.urls)),
] 