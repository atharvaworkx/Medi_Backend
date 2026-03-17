from django.urls import path, include
from rest_framework.routers import DefaultRouter
from medical.views import MedicalHistoryViewSet

router = DefaultRouter()
router.register(r'medical', MedicalHistoryViewSet, basename='medical')

urlpatterns = [
    path('', include(router.urls)),
]
