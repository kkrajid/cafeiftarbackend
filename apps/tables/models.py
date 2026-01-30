from django.db import models

class Table(models.Model):
    """
    Restaurant Table model
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    table_id = models.CharField(max_length=10)  # e.g., T1, P1
    name = models.CharField(max_length=50)
    seats = models.IntegerField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=100, blank=True, null=True)  # Main Hall, Window Side, etc.
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='tables'
    )
    x_position = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y_position = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tables'
        unique_together = ['table_id', 'branch']
        ordering = ['table_id']
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
    
    def __str__(self):
        return f"{self.table_id} - {self.name} ({self.branch.name})"
