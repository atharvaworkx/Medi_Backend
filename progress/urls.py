from django.urls import path, include
from rest_framework.routers import DefaultRouter
from progress.views import ProgressViewSet, SymptomViewSet

router = DefaultRouter()
router.register(r'progress', ProgressViewSet, basename='progress')
router.register(r'symptoms', SymptomViewSet, basename='symptom')

urlpatterns = [
    path('', include(router.urls)),
]
