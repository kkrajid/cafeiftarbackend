from django.contrib import admin
from .models import MenuItem, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_text', 'price', 'status', 'is_veg', 'is_spicy', 'is_featured', 'featured_order')
    list_filter = ('category_text', 'status', 'is_veg', 'is_spicy', 'is_featured')
    search_fields = ('name', 'description', 'category_text')
    list_editable = ('is_featured', 'featured_order')  # Quick toggle in list view
    ordering = ['category_text', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'category_text')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Details', {
            'fields': ('image', 'is_veg', 'is_spicy', 'status')
        }),
        ('Featured on Homepage', {
            'fields': ('is_featured', 'featured_order'),
            'description': 'Mark items to show in the Featured Dishes section on the landing page.'
        }),
    )
    
    actions = ['mark_featured', 'unmark_featured']
    
    @admin.action(description="Mark selected items as Featured")
    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} items marked as featured.")
    
    @admin.action(description="Remove from Featured")
    def unmark_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f"{count} items removed from featured.")

