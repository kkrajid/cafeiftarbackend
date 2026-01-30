from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Inquiry
from .serializers import InquirySerializer

class InquiryViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    filterset_fields = ['status']
    search_fields = ['name', 'email', 'subject']
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update inquiry status"""
        inquiry = self.get_object()
        status = request.data.get('status')
        if status in ['new', 'read', 'replied']:
            inquiry.status = status
            inquiry.save()
            return Response({'status': status})
        return Response({'error': 'Invalid status'}, status=400)
