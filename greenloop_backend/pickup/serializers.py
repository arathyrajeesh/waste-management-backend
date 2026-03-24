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
    assigned_worker_name = serializers.CharField(source='assigned_worker.username', read_only=True)

    class Meta:
        model = Pickup
        fields = [
            'id',
            'resident',
            'resident_name',
            'item',
            'item_display',
            'address',
            'scheduled_date',
            'location',
            'qr_code',
            'completed_at',
            'ward',
            'slot',
            'slot_display',
            'status',
            'assigned_worker',
            'assigned_worker_name',
            'fee_amount',
            'fee_paid',
            'waste_type',
            'weight_kg',
            'created_at'
        ]
        read_only_fields = ['resident']