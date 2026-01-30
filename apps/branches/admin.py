from django.contrib import admin
from .models import Branch, OperatingHours, SpecialDate


class OperatingHoursInline(admin.TabularInline):
    model = OperatingHours
    extra = 0
    ordering = ['day_of_week']


class SpecialDateInline(admin.TabularInline):
    model = SpecialDate
    extra = 0
    ordering = ['date']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'status', 'opening_time', 'closing_time', 'has_floor_plan', 'created_at')
    list_filter = ('status', 'has_floor_plan')
    search_fields = ('name', 'address', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OperatingHoursInline, SpecialDateInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'phone', 'hours', 'status')
        }),
        ('Default Operating Hours', {
            'fields': ('opening_time', 'closing_time', 'slot_duration', 'default_reservation_duration'),
            'description': 'These are fallback hours. Use the Operating Hours inline below for day-specific schedules.'
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'has_floor_plan', 'floor_plan'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('branch', 'day_of_week', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('branch', 'day_of_week', 'is_closed')
    ordering = ['branch', 'day_of_week']


@admin.register(SpecialDate)
class SpecialDateAdmin(admin.ModelAdmin):
    list_display = ('branch', 'date', 'type', 'is_closed', 'opening_time', 'closing_time', 'note')
    list_filter = ('branch', 'type', 'is_closed')
    search_fields = ('note',)
    ordering = ['-date']
    date_hierarchy = 'date'

