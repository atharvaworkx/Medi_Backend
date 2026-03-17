from django.urls import path
from rest_framework.routers import DefaultRouter
from consultations.views import ConsultationSessionViewSet

router = DefaultRouter()
router.register(r'', ConsultationSessionViewSet, basename='consultation')

urlpatterns = router.urls
