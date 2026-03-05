from rest_framework import serializers
from .models import Pickup

class PickupSerializer(serializers.ModelSerializer):

    resident_name = serializers.CharField(source='resident.username', read_only=True)

    class Meta:
        model = Pickup
        fields = [
            'id',
            'resident',
            'resident_name',
            'waste_type',
            'address',
            'date',
            'status',
            'created_at'
        ]
        read_only_fields = ['resident']