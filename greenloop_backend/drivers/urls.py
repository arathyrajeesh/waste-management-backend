from django.urls import path
from .views import AdminAddDriverView, UpdateDriverLocationView, DriverListView

urlpatterns = [
    path('add-driver/', AdminAddDriverView.as_view(), name='add-driver'),
    path('update-location/', UpdateDriverLocationView.as_view(), name='update-location'),
    path('list/', DriverListView.as_view(), name='driver-list'),
]
