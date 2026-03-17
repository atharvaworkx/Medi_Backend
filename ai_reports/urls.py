from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ai_reports.views import HealthAssessmentViewSet

router = DefaultRouter()
router.register(r'reports', HealthAssessmentViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
