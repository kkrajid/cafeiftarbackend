from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, date
from .models import Branch, OperatingHours, SpecialDate
from .serializers import (
    BranchSerializer, 
    BranchDetailSerializer,
    OperatingHoursSerializer, 
    SpecialDateSerializer,
    BranchHoursSerializer
)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'hours', 'hours_for_date']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BranchDetailSerializer
        return BranchSerializer
    
    @action(detail=True, methods=['get'])
    def hours(self, request, pk=None):
        """
        Get complete operating hours for a branch.
        Returns weekly schedule + upcoming special dates.
        """
        branch = self.get_object()
        
        weekly_hours = branch.operating_hours.all().order_by('day_of_week')
        special_dates = branch.special_dates.filter(
            date__gte=date.today()
        ).order_by('date')[:30]  # Next 30 special dates
        
        return Response({
            'branch_id': branch.id,
            'branch_name': branch.name,
            'default_opening': branch.opening_time.strftime('%H:%M'),
            'default_closing': branch.closing_time.strftime('%H:%M'),
            'slot_duration': branch.slot_duration,
            'weekly_hours': OperatingHoursSerializer(weekly_hours, many=True).data,
            'special_dates': SpecialDateSerializer(special_dates, many=True).data
        })
    
    @action(detail=True, methods=['get'], url_path='hours/(?P<target_date>[0-9-]+)')
    def hours_for_date(self, request, pk=None, target_date=None):
        """
        Get operating hours for a specific date.
        Handles day-of-week and special date overrides.
        """
        branch = self.get_object()
        
        # Parse the date
        try:
            parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Use the model's helper method
        hours_info = branch.get_hours_for_date(parsed_date)
        
        return Response({
            'branch_id': branch.id,
            'date': target_date,
            'day_of_week': parsed_date.strftime('%A'),
            'is_open': hours_info['is_open'],
            'opening_time': hours_info['opening_time'].strftime('%H:%M') if hours_info['opening_time'] else None,
            'closing_time': hours_info['closing_time'].strftime('%H:%M') if hours_info['closing_time'] else None,
            'note': hours_info.get('note')
        })


class OperatingHoursViewSet(viewsets.ModelViewSet):
    """Viewset for managing weekly operating hours - public read, admin write"""
    queryset = OperatingHours.objects.all()
    serializer_class = OperatingHoursSerializer
    filterset_fields = ['branch', 'day_of_week', 'is_closed']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class SpecialDateViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for managing special dates"""
    queryset = SpecialDate.objects.all()
    serializer_class = SpecialDateSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['branch', 'type', 'is_closed']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('date')
