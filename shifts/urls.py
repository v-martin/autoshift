from django.urls import path
from rest_framework.routers import DefaultRouter

from shifts.views import ShiftViewSet


router = DefaultRouter(trailing_slash=True)
router.register(r'shifts', ShiftViewSet)

urlpatterns = []

urlpatterns += router.urls 