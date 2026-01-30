from django.contrib import admin
from .models import Table

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'name', 'branch', 'seats', 'status', 'location')
    list_filter = ('status', 'branch')
    search_fields = ('table_id', 'name', 'location')
