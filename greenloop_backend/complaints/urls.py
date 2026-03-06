from django.urls import path
from .views import ComplaintViewSet

complaint_list = ComplaintViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

complaint_detail = ComplaintViewSet.as_view({
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('complaints/', complaint_list),
    path('complaints/<int:pk>/', complaint_detail),
]