from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GalleryImageViewSet

router = DefaultRouter()
router.register(r'', GalleryImageViewSet, basename='galleryimage')

urlpatterns = router.urls
