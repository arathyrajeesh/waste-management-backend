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

    serializer_class = PickupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        # Admin sees all pickups
        if user.role == "admin":
            return Pickup.objects.all()

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


