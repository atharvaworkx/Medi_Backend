from django.urls import path
from rest_framework.routers import DefaultRouter
from medicines.views import MedicineViewSet

router = DefaultRouter()
router.register(r'', MedicineViewSet, basename='medicine')

urlpatterns = router.urls
