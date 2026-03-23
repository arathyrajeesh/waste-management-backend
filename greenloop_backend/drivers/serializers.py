from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['latitude', 'longitude']

class DriverCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'ward']

    def create(self, validated_data):
        validated_data['role'] = 'driver'
        user = User.objects.create_user(**validated_data)
        return user

class DriverListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'latitude', 'longitude', 'phone', 'ward']
