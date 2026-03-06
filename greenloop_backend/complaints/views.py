from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Complaint
from .serializers import ComplaintSerializer


class ComplaintViewSet(viewsets.ModelViewSet):

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