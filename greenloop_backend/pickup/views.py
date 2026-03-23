from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pickup, PickupSlot
from .serializers import PickupSerializer, SlotSerializer
from notifications.models import Notification
from users.models import User

class PickupSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PickupSlot.objects.all()
    serializer_class = SlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PickupSlot.objects.all().order_by('date', 'start_time')
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        return queryset

    @action(detail=False, methods=['get'], url_path='available-dates')
    def available_dates(self, request):
        # Get unique dates from PickupSlot
        dates = PickupSlot.objects.values_list('date', flat=True).distinct().order_by('date')
        return Response(dates)

class PickupViewSet(viewsets.ModelViewSet):
    queryset = Pickup.objects.none()
    serializer_class = PickupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        
        # Admin sees all pickups
        if user.role == "admin":
            return Pickup.objects.all()
            
        # Worker sees only tasks assigned to them
        if user.role == "hks_worker":
            return Pickup.objects.filter(assigned_worker=user)

        # Resident sees only their pickups
        return Pickup.objects.filter(resident=user)


    def perform_create(self, serializer):

        pickup = serializer.save(resident=self.request.user)

        admins = User.objects.filter(role="admin")

        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Pickup Request",
                message=f"{self.request.user.username} requested waste pickup."
            )

    def perform_update(self, serializer):
        # Get the original object to see if the worker changed
        old_instance = self.get_object()
        old_worker = old_instance.assigned_worker
        
        pickup = serializer.save()
        
        # If a worker was assigned/changed, notify them
        new_worker = pickup.assigned_worker
        if new_worker and new_worker != old_worker:
            Notification.objects.create(
                user=new_worker,
                title="New Task Assigned",
                message=f"You have been assigned to a pickup for {pickup.resident.username} at {pickup.address}."
            )

    @action(detail=False, methods=['get'], url_path='available-workers')
    def available_workers(self, request):
        if request.user.role != "admin":
            return Response({"error": "Access denied"}, status=403)
            
        workers = User.objects.filter(role='hks_worker')
        from users.serializers import UserSerializer
        serializer = UserSerializer(workers, many=True)
        return Response(serializer.data)


