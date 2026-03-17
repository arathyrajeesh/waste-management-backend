from rest_framework import serializers
from .models import Pickup, PickupSlot

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupSlot
        fields = ['id', 'date', 'start_time', 'end_time']

class PickupSerializer(serializers.ModelSerializer):

    resident_name = serializers.CharField(source='resident.username', read_only=True)
    item_display = serializers.CharField(source='get_item_display', read_only=True)
    slot_display = serializers.StringRelatedField(source='slot', read_only=True)

    class Meta:
        model = Pickup
        fields = [
            'id',
            'resident',
            'resident_name',
            'item',
            'item_display',
            'address',
            'date',
            'slot',
            'slot_display',
            'status',
            'created_at'
        ]
        read_only_fields = ['resident']