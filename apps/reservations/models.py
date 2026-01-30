from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


class Reservation(models.Model):
    """
    Table Reservation model with smart duration calculation
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    confirmation_id = models.CharField(max_length=20, unique=True, editable=False)
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    table = models.ForeignKey(
        'tables.Table',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    
    # Reservation timing
    date = models.DateField()
    time = models.TimeField()  # Start time
    end_time = models.TimeField(null=True, blank=True)  # Auto-calculated end time
    duration_minutes = models.IntegerField(
        default=90,
        validators=[MinValueValidator(30), MaxValueValidator(180)],
        help_text="Reservation duration in minutes"
    )
    
    guests = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Number of guests (1-20)"
    )
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def calculate_duration_from_guests(guests: int) -> int:
        """
        Calculate reservation duration based on party size.
        Larger parties typically need more time.
        
        Returns duration in minutes.
        """
        if guests <= 2:
            return 60  # 1 hour for small parties
        elif guests <= 4:
            return 90  # 1.5 hours for medium parties
        elif guests <= 8:
            return 120  # 2 hours for larger parties
        else:
            return 150  # 2.5 hours for very large parties (9-20)
    
    def calculate_end_time(self):
        """Calculate end time from start time and duration"""
        if self.time and self.duration_minutes:
            start_dt = datetime.combine(datetime.today(), self.time)
            end_dt = start_dt + timedelta(minutes=self.duration_minutes)
            return end_dt.time()
        return None
    
    def clean(self):
        """Validate reservation data"""
        super().clean()
        
        # Prevent booking past dates - ONLY for new instances or if date changed
        is_new = self._state.adding
        has_date_changed = False
        
        if not is_new:
            original = Reservation.objects.get(pk=self.pk)
            if original.date != self.date:
                has_date_changed = True
            
            # If status is being changed to terminal states, allow past dates
            if self.status in ['cancelled', 'completed', 'no_show']:
                pass
            # Otherwise, enforce date validation only if date changed
            elif has_date_changed:
                if self.date < timezone.now().date():
                    raise ValidationError({'date': 'Cannot book reservations for past dates'})
        else:
            # For new reservations, always enforce future dates
            if self.date and self.date < timezone.now().date():
                raise ValidationError({'date': 'Cannot book reservations for past dates'})
        
        # Prevent booking past times on the same day - ONLY for new or modified time
        if self.date and self.date == timezone.now().date():
            if self.time and self.time <= timezone.now().time():
                # Allow if it's an existing record and we're not changing time
                if is_new or (not is_new and Reservation.objects.get(pk=self.pk).time != self.time):
                     raise ValidationError({'time': 'Cannot book reservations for past times'})
        
        # Validate guest count against table capacity
        if self.table and self.guests > self.table.seats:
            raise ValidationError({
                'guests': f'Table seats only {self.table.seats} guests, requested {self.guests}'
            })
        
        # Validate end time doesn't exceed branch closing time
        if self.branch and self.end_time and self.branch.closing_time:
            # Handle day overflow - if end_time is early morning, it's likely next day
            if self.end_time > self.branch.closing_time and self.end_time.hour < 6:
                pass  # Allow early morning overflow
            elif self.end_time > self.branch.closing_time:
                raise ValidationError({
                    'time': f'Reservation would extend past closing time ({self.branch.closing_time})'
                })
    
    def save(self, *args, **kwargs):
        # Auto-calculate duration based on guest count ONLY for new reservations
        # or if duration was never set (is default)
        is_new = self._state.adding
        if is_new and (not self.duration_minutes or self.pk is None):
            self.duration_minutes = self.calculate_duration_from_guests(self.guests)
        
        # Calculate end time
        self.end_time = self.calculate_end_time()
        
        # Generate confirmation ID
        if not self.confirmation_id:
            while True:
                conf_id = f"CI{uuid.uuid4().hex[:12].upper()}"
                if not Reservation.objects.filter(confirmation_id=conf_id).exists():
                    self.confirmation_id = conf_id
                    break
        
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'reservations'
        ordering = ['-created_at']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['branch', 'date']),
            models.Index(fields=['table', 'date', 'time', 'end_time']),
        ]
    
    def __str__(self):
        return f"{self.confirmation_id} - {self.customer_name}"

