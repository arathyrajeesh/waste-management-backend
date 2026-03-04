from django.urls import path
from .views import PickupViewSet

pickup_list = PickupViewSet.as_view({
    'get':'list',
    'post':'create'
})

urlpatterns = [
    path('pickups/', pickup_list),
]