"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import views, generics
from doctors.views import DoctorViewSet, SpecializationViewSet
from appointments.views import AppointmentViewSet, DoctorAvailabilityViewSet
from medicines.views import MedicineViewSet
from orders.views import OrderViewSet, SubscriptionViewSet
# NOTE: consultations, chatbot, prescriptions, ai_reports not yet wired to Flutter
# Uncomment when ready:
# from consultations.views import ConsultationSessionViewSet
# from chatbot.views import ChatMessageViewSet
# from prescriptions.views import PrescriptionViewSet

# Initialize router for core apps
router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'specializations', SpecializationViewSet, basename='specialization')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'availability', DoctorAvailabilityViewSet, basename='availability')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
# NOTE: progress & symptoms are registered in progress/urls.py to avoid duplicates
# NOTE: consultations, chatbot, prescriptions routes commented out until Flutter integration ready
# router.register(r'consultations', ConsultationSessionViewSet, basename='consultation')
# router.register(r'consultation-chat', ChatMessageViewSet, basename='chat')
# router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')


# admin.site.__class__ = OTPAdminSite

schema_view = get_schema_view(
    openapi.Info(
        title="Medico API",
        default_version='v1',
        description="AyuPilot — Personalized Ayurvedic Care API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@medipilot.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


class Home(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return views.Response(
            {
                "message": "Welcome to Atomicloops"
            }
        )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('profiles.urls')),
    path('api/v1/', include('medical.urls')),
    path('api/v1/', include('images.urls')),
    path('api/v1/', include('quiz.urls')),
    path('api/v1/', include('ai_reports.urls')),
    path('api/v1/', include('progress.urls')),  # includes progress/ and symptoms/ routes
    path('api/v1/', include(router.urls)),
    path('drf-auth/', include('rest_framework.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('postman.json/', schema_view.without_ui(cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("", Home.as_view()),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
