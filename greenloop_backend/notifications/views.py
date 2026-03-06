from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from pickup.models import Pickup
from pickup.serializers import PickupSerializer

from complaints.models import Complaint
from complaints.serializers import ComplaintSerializer

from notifications.models import Notification
from notifications.serializers import NotificationSerializer

from users.models import User

class ComplaintViewSet(viewsets.ModelViewSet):

    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role == "admin":
            return Complaint.objects.all()

        return Complaint.objects.filter(resident=user)


    def perform_create(self, serializer):

        complaint = serializer.save(resident=self.request.user)

        admins = User.objects.filter(role="admin")

        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Complaint",
                message=f"{self.request.user.username} submitted a complaint."
            )

class PickupViewSet(viewsets.ModelViewSet):

    serializer_class = PickupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role == "admin":
            return Pickup.objects.all()

        return Pickup.objects.filter(resident=user)


    def perform_create(self, serializer):

        pickup = serializer.save(resident=self.request.user)

        admins = User.objects.filter(role="admin")

        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Pickup Request",
                message=f"{self.request.user.username} requested a waste pickup."
            )

class NotificationViewSet(viewsets.ModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)