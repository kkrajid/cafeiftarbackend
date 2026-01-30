from django.db import models

class GalleryImage(models.Model):
    """
    Gallery Image model
    """
    CATEGORY_CHOICES = [
        ('culinary', 'Culinary'),
        ('ambience', 'Ambience'),
        ('moments', 'Moments'),
    ]
    
    image = models.ImageField(upload_to='gallery/', null=True, blank=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    caption = models.CharField(max_length=200)
    date_added = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'gallery_images'
        ordering = ['-date_added']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
    
    def __str__(self):
        return f"{self.caption} ({self.get_category_display()})"
