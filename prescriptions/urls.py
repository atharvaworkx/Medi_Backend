from django.urls import path
from rest_framework.routers import DefaultRouter
from prescriptions.views import PrescriptionViewSet

router = DefaultRouter()
router.register(r'', PrescriptionViewSet, basename='prescription')

urlpatterns = router.urls
