from rest_framework import serializers
from .models import Pickup


class PickupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pickup
        fields = '__all__'
        read_only_fields = ['resident']