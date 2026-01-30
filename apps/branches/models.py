from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from datetime import time, date

class Branch(models.Model):
    """
    Restaurant Branch model
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Enter a valid phone number (9-15 digits, optional + prefix)'
        )]
    )
    hours = models.CharField(max_length=100, blank=True, null=True)  # Legacy text field for display
    
    # Default operating hours (fallback if no OperatingHours exist)
    opening_time = models.TimeField(default=time(11, 0))  # 11:00 AM default
    closing_time = models.TimeField(default=time(22, 0))  # 10:00 PM default
    
    # Reservation settings
    slot_duration = models.IntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(60)],
        help_text="Time slot interval in minutes (15-60)"
    )
    default_reservation_duration = models.IntegerField(
        default=90,
        validators=[MinValueValidator(30), MaxValueValidator(180)],
        help_text="Default reservation duration in minutes (30-180)"
    )
    
    # Fixed precision: ±90.123456 for lat, ±180.123456 for long
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    has_floor_plan = models.BooleanField(default=False)
    floor_plan = models.ImageField(upload_to='floor_plans/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'branches'
        ordering = ['name']
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
    
    def __str__(self):
        return self.name
    
    def get_hours_for_date(self, target_date: date) -> dict:
        """
        Get operating hours for a specific date.
        Priority: SpecialDate > OperatingHours (day of week) > Default fields
        
        Returns dict with: is_open, opening_time, closing_time, note
        """
        # 1. Check for special date override
        special = self.special_dates.filter(date=target_date).first()
        if special:
            if special.is_closed:
                return {
                    'is_open': False,
                    'opening_time': None,
                    'closing_time': None,
                    'note': special.note or 'Closed'
                }
            return {
                'is_open': True,
                'opening_time': special.opening_time,
                'closing_time': special.closing_time,
                'note': special.note
            }
        
        # 2. Check for day-specific hours
        day_of_week = target_date.weekday()  # Monday = 0, Sunday = 6
        day_hours = self.operating_hours.filter(day_of_week=day_of_week).first()
        if day_hours:
            if day_hours.is_closed:
                return {
                    'is_open': False,
                    'opening_time': None,
                    'closing_time': None,
                    'note': 'Closed on this day'
                }
            return {
                'is_open': True,
                'opening_time': day_hours.opening_time,
                'closing_time': day_hours.closing_time,
                'note': None
            }
        
        # 3. Fallback to default branch hours
        return {
            'is_open': True,
            'opening_time': self.opening_time,
            'closing_time': self.closing_time,
            'note': None
        }


class OperatingHours(models.Model):
    """
    Weekly operating hours per day of week.
    Allows different hours for each day (e.g., shorter Sunday hours).
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='operating_hours'
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False, help_text="Mark as closed for this day")
    
    class Meta:
        db_table = 'branch_operating_hours'
        unique_together = ['branch', 'day_of_week']
        ordering = ['day_of_week']
        verbose_name = 'Operating Hours'
        verbose_name_plural = 'Operating Hours'
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES)[self.day_of_week]
        if self.is_closed:
            return f"{self.branch.name} - {day_name}: Closed"
        return f"{self.branch.name} - {day_name}: {self.opening_time} - {self.closing_time}"


class SpecialDate(models.Model):
    """
    Special dates with custom hours or closures.
    Overrides both OperatingHours and default branch hours.
    
    Use cases:
    - Holidays (Eid, Christmas, New Year)
    - Ramadan timing
    - Private events
    - Maintenance closures
    """
    TYPE_CHOICES = [
        ('holiday', 'Holiday'),
        ('ramadan', 'Ramadan'),
        ('event', 'Private Event'),
        ('maintenance', 'Maintenance'),
        ('special', 'Special Hours'),
    ]
    
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='special_dates'
    )
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='special')
    is_closed = models.BooleanField(default=False, help_text="Completely closed on this date")
    opening_time = models.TimeField(null=True, blank=True, help_text="Leave blank if closed")
    closing_time = models.TimeField(null=True, blank=True, help_text="Leave blank if closed")
    note = models.CharField(max_length=200, blank=True, help_text="e.g., 'Eid Mubarak - Limited Menu'")
    
    class Meta:
        db_table = 'branch_special_dates'
        unique_together = ['branch', 'date']
        ordering = ['date']
        verbose_name = 'Special Date'
        verbose_name_plural = 'Special Dates'
    
    def __str__(self):
        status = "Closed" if self.is_closed else f"{self.opening_time} - {self.closing_time}"
        return f"{self.branch.name} - {self.date}: {status}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.is_closed and (not self.opening_time or not self.closing_time):
            raise ValidationError("Opening and closing times are required unless marked as closed")


