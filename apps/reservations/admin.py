from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('confirmation_id', 'customer_name', 'branch', 'table', 'date', 'time', 'guests', 'status')
    list_filter = ('status', 'branch', 'date')
    search_fields = ('confirmation_id', 'customer_name', 'phone', 'email')
    readonly_fields = ('confirmation_id', 'created_at', 'updated_at')
    date_hierarchy = 'date'
