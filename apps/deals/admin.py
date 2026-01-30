from django.contrib import admin
from .models import Deal

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'discount_display', 'valid_from', 'valid_until', 'status', 'tag')
    list_filter = ('status', 'discount_type', 'tag')
    search_fields = ('title', 'code', 'description')

