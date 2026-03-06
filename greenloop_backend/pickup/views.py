from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Pickup
from .serializers import PickupSerializer
from notifications.models import Notification
from users.models import User

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


