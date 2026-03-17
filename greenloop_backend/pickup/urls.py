from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PickupViewSet, PickupSlotViewSet

router = DefaultRouter()
router.register(r'pickups', PickupViewSet, basename='pickup')
router.register(r'pickup-slots', PickupSlotViewSet, basename='pickup-slot')

urlpatterns = [
    path('', include(router.urls)),
]