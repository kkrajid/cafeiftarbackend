from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Deal(models.Model):
    """
    Promotional Deal model
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    code = models.CharField(max_length=20, unique=True)
    
    # Structured discount instead of free text
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Percentage (0-100) or fixed amount",
        null=True, blank=True
    )
    
    # Price fields for "Was/Now" display
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Proper date fields instead of text
    valid_from = models.DateField()
    valid_until = models.DateField()
    
    image = models.ImageField(upload_to='deals/', null=True, blank=True)
    tag = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def clean(self):
        """Validate deal dates"""
        super().clean()
        if self.valid_from and self.valid_until:
            if self.valid_from > self.valid_until:
                raise ValidationError({'valid_until': 'End date must be after start date'})
    
    def is_valid(self):
        """Check if deal is currently valid"""
        today = timezone.now().date()
        return (
            self.status == 'active' and 
            self.valid_from <= today <= self.valid_until
        )

    def save(self, *args, **kwargs):
        # Auto-calculate discount value if prices are set
        if self.original_price and self.discounted_price:
            self.discount_value = self.original_price - self.discounted_price
            self.discount_type = 'fixed'
        super().save(*args, **kwargs)
    
    @property
    def discount_display(self):
        """Display discount in readable format"""
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% OFF"
        else:
            return f"₹{self.discount_value} OFF"
    
    class Meta:
        db_table = 'deals'
        ordering = ['-created_at']
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'
        indexes = [
            models.Index(fields=['valid_from', 'valid_until', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.code}) - {self.discount_display}"
