from django.urls import path
from .views import (
    DashboardStatsView,
    ReservationTrendsView,
    BranchPerformanceView,
    MenuAnalyticsView,
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('stats/reservation-trends/', ReservationTrendsView.as_view(), name='reservation_trends'),
    path('stats/branch-performance/', BranchPerformanceView.as_view(), name='branch_performance'),
    path('stats/menu-analytics/', MenuAnalyticsView.as_view(), name='menu_analytics'),
]
