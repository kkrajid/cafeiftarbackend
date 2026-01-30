from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Deal
from .serializers import DealSerializer

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    filterset_fields = ['status', 'tag']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'validate']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate a promo code"""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code required'}, status=400)
        
        try:
            deal = Deal.objects.get(code=code, status='active')
            serializer = self.get_serializer(deal)
            return Response({
                'valid': True,
                'deal': serializer.data
            })
        except Deal.DoesNotExist:
            return Response({'valid': False, 'error': 'Invalid or expired code'}, status=404)
