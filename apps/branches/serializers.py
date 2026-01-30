from rest_framework import serializers
from .models import Branch, OperatingHours, SpecialDate


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class OperatingHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OperatingHours
        fields = ['id', 'branch', 'day_of_week', 'day_name', 'opening_time', 'closing_time', 'is_closed']
    
    def get_day_name(self, obj):
        return dict(OperatingHours.DAY_CHOICES).get(obj.day_of_week, '')


class SpecialDateSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SpecialDate
        fields = ['id', 'branch', 'date', 'type', 'type_display', 'is_closed', 'opening_time', 'closing_time', 'note']
    
    def get_type_display(self, obj):
        return dict(SpecialDate.TYPE_CHOICES).get(obj.type, '')


class BranchHoursSerializer(serializers.Serializer):
    """Combined serializer for branch operating hours"""
    branch_id = serializers.IntegerField()
    branch_name = serializers.CharField()
    default_opening = serializers.TimeField()
    default_closing = serializers.TimeField()
    weekly_hours = OperatingHoursSerializer(many=True)
    special_dates = SpecialDateSerializer(many=True)


class BranchDetailSerializer(serializers.ModelSerializer):
    """Extended branch serializer with hours info"""
    operating_hours = OperatingHoursSerializer(many=True, read_only=True)
    upcoming_special_dates = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = '__all__'
    
    def get_upcoming_special_dates(self, obj):
        from datetime import date
        upcoming = obj.special_dates.filter(date__gte=date.today()).order_by('date')[:10]
        return SpecialDateSerializer(upcoming, many=True).data

