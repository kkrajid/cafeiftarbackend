from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, OperatingHoursViewSet, SpecialDateViewSet

# Create separate routers for proper URL matching
# Specific routes must be registered on separate routers or ordered properly
router = DefaultRouter()

# Register these FIRST (specific routes)
router.register(r'operating-hours', OperatingHoursViewSet, basename='operating-hours')
router.register(r'special-dates', SpecialDateViewSet, basename='special-dates')

# Register branch router LAST (catch-all with empty prefix)
router.register(r'', BranchViewSet, basename='branch')

urlpatterns = router.urls


