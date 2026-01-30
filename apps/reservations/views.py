from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Reservation
from .serializers import ReservationSerializer, ReservationCreateSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    filterset_fields = ['branch', 'status', 'date']
    search_fields = ['confirmation_id', 'customer_name', 'phone', 'email']
    
    def get_permissions(self):
        if self.action in ['create', 'by_confirmation', 'my_reservations']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer
    
    def perform_create(self, serializer):
        """Create reservation with proper error handling"""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError
        
        try:
            reservation = serializer.save()
            # Send confirmation email
            self.send_confirmation_email(reservation)
        except ValidationError as e:
            # Convert ValidationError to DRF error
            from rest_framework.exceptions import ValidationError as DRFValidationError
            raise DRFValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))
        except IntegrityError:
            from rest_framework.exceptions import ValidationError as DRFValidationError
            raise DRFValidationError({'error': 'This table is already booked for the selected date and time'})
    
    def send_confirmation_email(self, reservation):
        """Send reservation confirmation email"""
        import logging
        logger = logging.getLogger(__name__)
        
        subject = f"Reservation Confirmation - {reservation.confirmation_id}"
        message = f"""
        Dear {reservation.customer_name},
        
        Your table reservation has been confirmed!
        
        Confirmation ID: {reservation.confirmation_id}
        Branch: {reservation.branch.name}
        Date: {reservation.date}
        Time: {reservation.time}
        Guests: {reservation.guests}
        Table: {reservation.table.name if reservation.table else 'TBD'}
        
        We look forward to serving you!
        
        Café Iftar
        {reservation.branch.address}
        {reservation.branch.phone}
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.email],
                fail_silently=False,
            )
            logger.info(f"Confirmation email sent for {reservation.confirmation_id}")
        except Exception as e:
            logger.error(f"Failed to send email for {reservation.confirmation_id}: {e}")
    
    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Admin confirms a reservation"""
        reservation = self.get_object()
        reservation.status = 'confirmed'
        reservation.save(update_fields=['status'])
        return Response({'status': 'confirmed', 'confirmation_id': reservation.confirmation_id})
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Admin cancels a reservation"""
        reservation = self.get_object()
        reservation.status = 'cancelled'
        reservation.save(update_fields=['status'])
        return Response({'status': 'cancelled', 'confirmation_id': reservation.confirmation_id})
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """Mark reservation as completed (customer finished dining)"""
        reservation = self.get_object()
        if reservation.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed reservations can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservation.status = 'completed'
        reservation.save(update_fields=['status'])
        return Response({'status': 'completed', 'confirmation_id': reservation.confirmation_id})
    
    @action(detail=True, methods=['patch'])
    def noshow(self, request, pk=None):
        """Mark reservation as no-show (customer didn't arrive)"""
        reservation = self.get_object()
        if reservation.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Only pending or confirmed reservations can be marked as no-show'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservation.status = 'no_show'
        reservation.save(update_fields=['status'])
        return Response({'status': 'no_show', 'confirmation_id': reservation.confirmation_id})
    
    @action(detail=False, methods=['get'])
    def by_confirmation(self, request):
        """Look up reservation by confirmation ID - returns limited public info"""
        conf_id = request.query_params.get('confirmation_id')
        if not conf_id:
            return Response({'error': 'confirmation_id required'}, status=400)
        
        try:
            reservation = Reservation.objects.select_related('branch', 'table').get(confirmation_id=conf_id)
            # Return limited info for public lookup (no phone/email exposed)
            return Response({
                'confirmation_id': reservation.confirmation_id,
                'branch_name': reservation.branch.name if reservation.branch else None,
                'table_name': reservation.table.name if reservation.table else None,
                'date': reservation.date,
                'time': reservation.time,
                'guests': reservation.guests,
                'status': reservation.status,
                'customer_name': reservation.customer_name,  # Show name for verification
            })
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=404)
    
    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        """
        Get reservations for a customer by email or phone.
        Public endpoint for customers to view their bookings.
        """
        email = request.query_params.get('email')
        phone = request.query_params.get('phone')
        
        if not email and not phone:
            return Response(
                {'error': 'email or phone is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build query
        query = Q()
        if email:
            query |= Q(email__iexact=email)
        if phone:
            query |= Q(phone=phone)
        
        reservations = Reservation.objects.filter(query).order_by('-date', '-time')[:20]
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's reservations for a branch (admin dashboard)"""
        from datetime import date
        
        branch_id = request.query_params.get('branch')
        if not branch_id:
            return Response({'error': 'branch is required'}, status=400)
        
        reservations = Reservation.objects.filter(
            branch_id=branch_id,
            date=date.today()
        ).exclude(status='cancelled').order_by('time')
        
        serializer = self.get_serializer(reservations, many=True)
        return Response({
            'date': date.today().isoformat(),
            'branch_id': int(branch_id),
            'count': reservations.count(),
            'reservations': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get reservation statistics for admin dashboard"""
        from datetime import date, timedelta
        from django.db.models import Count
        
        branch_id = request.query_params.get('branch')
        
        # Base queryset
        qs = Reservation.objects.all()
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        
        today = date.today()
        
        # Calculate stats
        stats = {
            'today': qs.filter(date=today).exclude(status='cancelled').count(),
            'pending': qs.filter(status='pending').count(),
            'confirmed': qs.filter(status='confirmed').count(),
            'completed_this_week': qs.filter(
                status='completed',
                date__gte=today - timedelta(days=7)
            ).count(),
            'no_shows_this_week': qs.filter(
                status='no_show',
                date__gte=today - timedelta(days=7)
            ).count(),
            'upcoming': qs.filter(
                date__gte=today,
                status__in=['pending', 'confirmed']
            ).count(),
        }
        
        # Status breakdown
        status_counts = qs.values('status').annotate(count=Count('id'))
        stats['by_status'] = {item['status']: item['count'] for item in status_counts}
        
        return Response(stats)

