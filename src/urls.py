from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from doctors.views import DoctorViewSet, SpecializationViewSet
from appointments.views import AppointmentViewSet, DoctorAvailabilityViewSet
from medicines.views import MedicineViewSet
from orders.views import OrderViewSet, SubscriptionViewSet


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'service': 'ayupilot-backend',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)


router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'specializations', SpecializationViewSet, basename='specialization')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'availability', DoctorAvailabilityViewSet, basename='availability')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')


schema_view = get_schema_view(
    openapi.Info(
        title="AyuPilot API",
        default_version='v1',
        description="AyuPilot — Personalized Ayurvedic Care API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@ayupilot.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('profiles.urls')),
    path('api/v1/', include('medical.urls')),
    path('api/v1/', include('images.urls')),
    path('api/v1/', include('quiz.urls')),
    path('api/v1/', include('ai_reports.urls')),
    path('api/v1/', include('progress.urls')),
    path('api/v1/', include(router.urls)),
    path('drf-auth/', include('rest_framework.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('postman.json/', schema_view.without_ui(cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
