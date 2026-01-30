from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Table
from .serializers import TableSerializer
from datetime import datetime, timedelta, time


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filterset_fields = ['branch', 'status']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'availability', 'available_slots']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """Check available tables for a specific date, time, and guest count"""
        from apps.reservations.models import Reservation
        from apps.branches.models import Branch
        
        branch_id = request.query_params.get('branch')
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')
        guests_param = request.query_params.get('guests', '1')
        
        if not all([branch_id, date_str, time_str]):
            return Response({'error': 'branch, date, and time are required'}, status=400)
        
        # Validate guests
        try:
            guests = int(guests_param)
            if guests < 1 or guests > 20:
                return Response({'error': 'guests must be between 1 and 20'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'guests must be a valid number'}, status=400)
        
        # Validate time format
        try:
            booking_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return Response({'error': 'Invalid time format. Use HH:MM'}, status=400)
        
        # Parse date for same-day validation
        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Prevent booking past times on same day
        from django.utils import timezone
        now = timezone.now()
        if booking_date == now.date() and booking_time <= now.time():
            return Response({'error': 'Cannot book for past times'}, status=400)
        
        # Get branch for duration calculation
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=404)
        
        # Get tables for branch with enough seats
        tables = Table.objects.filter(
            branch_id=branch_id,
            status='active',
            seats__gte=guests
        )
        
        # Calculate reservation duration for requested party size
        duration = Reservation.calculate_duration_from_guests(guests)
        
        # Calculate time window for new reservation
        start_dt = datetime.combine(booking_date, booking_time)
        end_dt = start_dt + timedelta(minutes=duration)
        new_start = booking_time
        new_end = end_dt.time()
        
        # Find tables with overlapping reservations
        # Handle NULL end_time by calculating it from time + duration_minutes
        reserved_table_ids = set()
        existing_reservations = Reservation.objects.filter(
            branch_id=branch_id,
            date=date_str,
            status__in=['pending', 'confirmed']
        ).values('table_id', 'time', 'end_time', 'duration_minutes')
        
        for res in existing_reservations:
            res_start = res['time']
            res_end = res['end_time']
            
            # Calculate end_time if NULL
            if res_end is None and res_start and res['duration_minutes']:
                res_start_dt = datetime.combine(booking_date, res_start)
                res_end = (res_start_dt + timedelta(minutes=res['duration_minutes'])).time()
            
            # Check overlap: new_start < res_end AND res_start < new_end
            if res_start and res_end:
                if new_start < res_end and res_start < new_end:
                    reserved_table_ids.add(res['table_id'])
        
        available_tables = tables.exclude(id__in=reserved_table_ids)
        
        serializer = self.get_serializer(available_tables, many=True)
        return Response({
            'available': available_tables.exists(),
            'tables': serializer.data,
            'total_available': available_tables.count(),
            'requested_time': time_str,
            'reservation_duration_minutes': duration
        })
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Get available time slots for a given date, branch, and party size.
        Returns slots grouped by meal period (Lunch, Afternoon, Dinner).
        Uses Branch.get_hours_for_date() for flexible operating hours.
        """
        from apps.reservations.models import Reservation
        from apps.branches.models import Branch
        from datetime import date as date_type
        
        branch_id = request.query_params.get('branch')
        date_str = request.query_params.get('date')
        guests_param = request.query_params.get('guests', '2')
        
        if not all([branch_id, date_str]):
            return Response({'error': 'branch and date are required'}, status=400)
        
        # Parse and validate date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Validate guests
        try:
            guests = int(guests_param)
            if guests < 1 or guests > 20:
                return Response({'error': 'guests must be between 1 and 20'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'guests must be a valid number'}, status=400)
        
        # Get branch
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=404)
        
        # Get operating hours for the specific date (handles day-of-week and special dates)
        hours_info = branch.get_hours_for_date(target_date)
        
        # Check if closed
        if not hours_info['is_open']:
            return Response({
                'date': date_str,
                'branch_id': int(branch_id),
                'guests': guests,
                'is_closed': True,
                'note': hours_info.get('note', 'Closed'),
                'slots': {'lunch': [], 'afternoon': [], 'dinner': []}
            })
        
        # Calculate duration for party size
        duration = Reservation.calculate_duration_from_guests(guests)
        
        # Generate time slots from opening to closing time
        slot_interval = branch.slot_duration  # in minutes
        opening = datetime.combine(datetime.today(), hours_info['opening_time'])
        closing = datetime.combine(datetime.today(), hours_info['closing_time'])
        
        # Get tables that can accommodate the party
        suitable_tables = Table.objects.filter(
            branch=branch,
            status='active',
            seats__gte=guests
        ).count()
        
        if suitable_tables == 0:
            return Response({'error': 'No suitable tables found for this party size'}, status=404)
        
        # Get existing reservations for the date (include duration_minutes for fallback)
        existing_reservations = list(Reservation.objects.filter(
            branch=branch,
            date=date_str,
            status__in=['pending', 'confirmed']
        ).select_related('table').values('table_id', 'time', 'end_time', 'duration_minutes'))
        
        # Generate slots and check availability
        available_slots = {
            'lunch': [],      # Before 2:30 PM
            'afternoon': [],  # 2:30 PM - 5:00 PM
            'dinner': []      # 5:00 PM onwards
        }
        
        current = opening
        while current + timedelta(minutes=duration) <= closing:
            slot_time = current.time()
            slot_end = (current + timedelta(minutes=duration)).time()
            
            # Count available tables for this slot
            available_count = suitable_tables
            for res in existing_reservations:
                # Check overlap with each reservation
                res_start = res['time']
                res_end = res['end_time']
                
                # Calculate end_time if NULL (fallback using duration_minutes)
                if res_end is None and res_start and res['duration_minutes']:
                    res_start_dt = datetime.combine(target_date, res_start)
                    res_end = (res_start_dt + timedelta(minutes=res['duration_minutes'])).time()
                
                # Overlap check: slot_start < res_end AND res_start < slot_end
                if res_start and res_end:
                    if slot_time < res_end and res_start < slot_end:
                        available_count -= 1
            
            if available_count > 0:
                slot_data = {
                    'time': slot_time.strftime('%H:%M'),
                    'display': self._format_time_display(slot_time),
                    'available_tables': available_count,
                    'duration_minutes': duration
                }
                
                # Categorize by meal period
                hour = slot_time.hour
                if hour < 14 or (hour == 14 and slot_time.minute < 30):
                    available_slots['lunch'].append(slot_data)
                elif hour < 17:
                    available_slots['afternoon'].append(slot_data)
                else:
                    available_slots['dinner'].append(slot_data)
            
            current += timedelta(minutes=slot_interval)
        
        return Response({
            'date': date_str,
            'branch_id': int(branch_id),
            'guests': guests,
            'duration_minutes': duration,
            'is_closed': False,
            'note': hours_info.get('note'),
            'opening_time': hours_info['opening_time'].strftime('%H:%M') if hours_info['opening_time'] else None,
            'closing_time': hours_info['closing_time'].strftime('%H:%M') if hours_info['closing_time'] else None,
            'slots': available_slots
        })
    
    def _format_time_display(self, t):
        """Format time as 12-hour display (e.g., '11:30 AM')"""
        hour = t.hour
        minute = t.minute
        period = 'AM' if hour < 12 else 'PM'
        if hour == 0:
            hour = 12
        elif hour > 12:
            hour -= 12
        return f"{hour}:{minute:02d} {period}"


