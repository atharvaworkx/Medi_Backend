from django.urls import path, include
from rest_framework.routers import DefaultRouter
from images.views import HealthImageViewSet

router = DefaultRouter()
router.register(r'images', HealthImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),
]
