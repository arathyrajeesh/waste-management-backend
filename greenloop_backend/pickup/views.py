from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Pickup
from .serializers import PickupSerializer


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
        serializer.save(resident=self.request.user)

