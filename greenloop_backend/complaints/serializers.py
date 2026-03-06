from rest_framework import serializers
from .models import Complaint

class ComplaintSerializer(serializers.ModelSerializer):

    resident_name = serializers.CharField(source='resident.username', read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id',
            'resident',
            'resident_name',
            'title',
            'description',
            'status',
            'created_at'
        ]
        read_only_fields = ['resident']