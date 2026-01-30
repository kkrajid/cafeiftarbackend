from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    table_name = serializers.CharField(source='table.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('confirmation_id', 'created_at', 'updated_at')

class ReservationCreateSerializer(serializers.ModelSerializer):
    confirmation_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Reservation
        fields = ('branch', 'table', 'customer_name', 'phone', 'email', 'date', 'time', 'guests', 'special_requests', 'confirmation_id')
        read_only_fields = ('confirmation_id',)

