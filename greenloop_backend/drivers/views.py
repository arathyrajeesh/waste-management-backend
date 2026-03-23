from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import DriverLocationSerializer, DriverCreateSerializer, DriverListSerializer

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsDriverUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'driver'

class AdminAddDriverView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = DriverCreateSerializer
    permission_classes = [IsAdminUser]

class UpdateDriverLocationView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = DriverLocationSerializer
    permission_classes = [IsDriverUser]

    def get_object(self):
        return self.request.user

class DriverListView(generics.ListAPIView):
    serializer_class = DriverListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(role='driver')
