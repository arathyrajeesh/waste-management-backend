from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Complaint
from .serializers import ComplaintSerializer


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.none()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        # Admin sees all complaints
        if user.role == "admin":
            return Complaint.objects.all()

        # Resident sees only their complaints
        return Complaint.objects.filter(resident=user)

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)

    def perform_update(self, serializer):
        # Check if assigned_worker changed and is not null
        old_complaint = self.get_object()
        new_worker = serializer.validated_data.get('assigned_worker', old_complaint.assigned_worker)
        
        instance = serializer.save()

        # If a worker is newly assigned or the assignment changes
        if new_worker and (old_complaint.assigned_worker != new_worker):
            from notifications.models import Notification
            Notification.objects.create(
                user=new_worker,
                title="New Complaint Assigned",
                message=f"You have been assigned to complaint: {instance.title}"
            )