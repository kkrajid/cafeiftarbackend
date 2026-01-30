"""
Admin Dashboard Stats Views
Provides comprehensive statistics for the admin dashboard
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta

from apps.reservations.models import Reservation
from apps.menu.models import MenuItem, Category
from apps.branches.models import Branch
from apps.tables.models import Table
from apps.inquiries.models import Inquiry
from apps.deals.models import Deal


class DashboardStatsView(APIView):
    """
    Comprehensive dashboard statistics for admin panel
    GET /api/admin/stats/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Reservation Stats
        reservations = Reservation.objects.all()
        today_reservations = reservations.filter(date=today)
        
        reservation_stats = {
            'today': {
                'total': today_reservations.count(),
                'pending': today_reservations.filter(status='pending').count(),
                'confirmed': today_reservations.filter(status='confirmed').count(),
                'completed': today_reservations.filter(status='completed').count(),
                'cancelled': today_reservations.filter(status='cancelled').count(),
                'no_show': today_reservations.filter(status='no_show').count(),
            },
            'week': reservations.filter(date__gte=week_ago).count(),
            'month': reservations.filter(date__gte=month_ago).count(),
            'total': reservations.count(),
            'upcoming': reservations.filter(date__gte=today, status__in=['pending', 'confirmed']).count(),
        }
        
        # Menu Stats
        menu_items = MenuItem.objects.all()
        menu_stats = {
            'total_items': menu_items.count(),
            'featured': menu_items.filter(is_featured=True).count(),
            'in_stock': menu_items.filter(status='in_stock').count(),
            'out_of_stock': menu_items.filter(status='out_of_stock').count(),
            'categories': Category.objects.count(),
            'veg_items': menu_items.filter(is_veg=True).count(),
            'non_veg_items': menu_items.filter(is_veg=False).count(),
        }
        
        # Branch Stats
        branches = Branch.objects.all()
        branch_stats = {
            'total': branches.count(),
            'active': branches.filter(status='active').count(),
            'inactive': branches.filter(status='inactive').count(),
        }
        
        # Table Stats
        tables = Table.objects.all()
        table_stats = {
            'total': tables.count(),
            'active': tables.filter(status='active').count(),
            'total_seats': tables.aggregate(total=Sum('seats'))['total'] or 0,
            'by_branch': list(tables.values('branch__name').annotate(
                count=Count('id'),
                seats=Sum('seats')
            )),
        }
        
        # Inquiry Stats
        inquiries = Inquiry.objects.all()
        inquiry_stats = {
            'total': inquiries.count(),
            'new': inquiries.filter(status='new').count(),
            'read': inquiries.filter(status='read').count(),
            'replied': inquiries.filter(status='replied').count(),
            'this_week': inquiries.filter(created_at__date__gte=week_ago).count(),
        }
        
        # Deal Stats
        deals = Deal.objects.all()
        deal_stats = {
            'total': deals.count(),
            'active': deals.filter(status='active').count(),
            'expired': deals.filter(valid_until__lt=today).count(),
        }
        
        return Response({
            'reservations': reservation_stats,
            'menu': menu_stats,
            'branches': branch_stats,
            'tables': table_stats,
            'inquiries': inquiry_stats,
            'deals': deal_stats,
            'generated_at': timezone.now().isoformat(),
        })


class ReservationTrendsView(APIView):
    """
    Reservation trends for charts
    GET /api/dashboard/stats/reservation-trends/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Daily reservation counts by date
        daily_data = (
            Reservation.objects
            .filter(date__gte=start_date)
            .values('date')
            .annotate(
                total=Count('id'),
                confirmed=Count('id', filter=Q(status='confirmed')),
                cancelled=Count('id', filter=Q(status='cancelled')),
                completed=Count('id', filter=Q(status='completed')),
            )
            .order_by('date')
        )
        
        # By status breakdown
        status_breakdown = (
            Reservation.objects
            .filter(date__gte=start_date)
            .values('status')
            .annotate(count=Count('id'))
        )
        
        # By branch
        by_branch = (
            Reservation.objects
            .filter(date__gte=start_date)
            .values('branch__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Average guests
        avg_guests = (
            Reservation.objects
            .filter(date__gte=start_date)
            .aggregate(avg=Avg('guests'))
        )
        
        # Total for period
        total_for_period = Reservation.objects.filter(date__gte=start_date).count()
        
        return Response({
            'daily': list(daily_data),
            'by_status': list(status_breakdown),
            'by_branch': list(by_branch),
            'average_guests': round(avg_guests['avg'] or 0, 1),
            'total_reservations': total_for_period,
            'period_days': days,
        })


class BranchPerformanceView(APIView):
    """
    Branch performance metrics
    GET /api/admin/stats/branch-performance/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        today = timezone.now().date()
        month_ago = today - timedelta(days=30)
        
        branches = Branch.objects.filter(status='active')
        performance = []
        
        for branch in branches:
            reservations = Reservation.objects.filter(
                branch=branch,
                date__gte=month_ago
            )
            
            total = reservations.count()
            completed = reservations.filter(status='completed').count()
            cancelled = reservations.filter(status='cancelled').count()
            no_shows = reservations.filter(status='no_show').count()
            
            performance.append({
                'branch_id': branch.id,
                'branch_name': branch.name,
                'total_reservations': total,
                'completed': completed,
                'cancelled': cancelled,
                'no_shows': no_shows,
                'completion_rate': round((completed / total * 100), 1) if total > 0 else 0,
                'cancellation_rate': round((cancelled / total * 100), 1) if total > 0 else 0,
                'tables_count': branch.tables.count(),
                'total_capacity': branch.tables.aggregate(total=Sum('seats'))['total'] or 0,
            })
        
        return Response({
            'branches': performance,
            'period': '30 days',
        })


class MenuAnalyticsView(APIView):
    """
    Menu analytics
    GET /api/admin/stats/menu-analytics/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Items by category
        by_category = (
            MenuItem.objects
            .values('category_text')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Price range distribution
        items = MenuItem.objects.all()
        price_ranges = {
            'under_100': items.filter(price__lt=100).count(),
            '100_to_300': items.filter(price__gte=100, price__lt=300).count(),
            '300_to_500': items.filter(price__gte=300, price__lt=500).count(),
            'above_500': items.filter(price__gte=500).count(),
        }
        
        # Featured items
        featured = MenuItem.objects.filter(is_featured=True).values(
            'id', 'name', 'price', 'category_text', 'featured_order'
        ).order_by('featured_order')
        
        return Response({
            'by_category': list(by_category),
            'price_distribution': price_ranges,
            'featured_items': list(featured),
            'total_items': items.count(),
        })

