from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'description']
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['category', 'category_text', 'status', 'is_veg', 'is_spicy', 'is_featured']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured menu items for landing page.
        Returns items marked as featured, ordered by featured_order.
        """
        limit = request.query_params.get('limit', 6)
        try:
            limit = int(limit)
        except ValueError:
            limit = 6
        
        featured_items = MenuItem.objects.filter(
            is_featured=True,
            status='in_stock'
        ).order_by('featured_order', '-created_at')[:limit]
        
        serializer = self.get_serializer(featured_items, many=True)
        return Response({
            'count': featured_items.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['patch'])
    def toggle_featured(self, request, pk=None):
        """Admin: Toggle featured status of a menu item"""
        item = self.get_object()
        item.is_featured = not item.is_featured
        item.save(update_fields=['is_featured'])
        return Response({
            'id': item.id,
            'name': item.name,
            'is_featured': item.is_featured
        })

