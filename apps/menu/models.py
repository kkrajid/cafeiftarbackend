from django.db import models
from django.core.validators import MinValueValidator

from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="Utensils")
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """
    Menu Item model
    """
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category_text = models.CharField(max_length=50, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    # Fixed: Price as decimal for calculations, not string
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price in INR"
    )
    currency = models.CharField(max_length=3, default='INR')
    image = models.ImageField(upload_to='menu/', null=True, blank=True)
    is_veg = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STOCK_STATUS, default='in_stock')
    
    # Featured on landing page
    is_featured = models.BooleanField(
        default=False, 
        help_text="Show this item in the Featured Dishes section on homepage"
    )
    featured_order = models.PositiveIntegerField(
        default=0,
        help_text="Order of appearance in featured section (lower = first)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['category_text', 'name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
    
    def save(self, *args, **kwargs):
        if self.category and not self.category_text:
            self.category_text = self.category.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category})"
