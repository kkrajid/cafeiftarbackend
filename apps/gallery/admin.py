from django.contrib import admin
from .models import GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'category', 'date_added')
    list_filter = ('category', 'date_added')
    search_fields = ('caption',)
