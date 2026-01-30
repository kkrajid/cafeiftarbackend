"""
URL Configuration for Cafe Iftar backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/branches/', include('apps.branches.urls')),
    path('api/tables/', include('apps.tables.urls')),
    path('api/reservations/', include('apps.reservations.urls')),
    path('api/menu/', include('apps.menu.urls')),
    path('api/deals/', include('apps.deals.urls')),
    path('api/inquiries/', include('apps.inquiries.urls')),
    path('api/gallery/', include('apps.gallery.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),  # Admin dashboard stats
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
