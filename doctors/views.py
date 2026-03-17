from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from doctors.models import Doctor, Specialization, DoctorAvailability
from doctors.serializers import (
    DoctorListSerializer,
    DoctorDetailSerializer,
    SpecializationSerializer,
    DoctorAvailabilitySerializer
)
from doctors.services.doctor_matching import DoctorMatchingService


class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """Specialization listing."""
    queryset = Specialization.objects.filter(is_active=True)
    serializer_class = SpecializationSerializer
    permission_classes = [IsAuthenticated]


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """Doctor listing and matching."""
    queryset = Doctor.objects.filter(
        is_available=True,
        is_verified=True
    ).select_related('specialization', 'user').prefetch_related('availability_slots')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DoctorDetailSerializer
        return DoctorListSerializer
    
    @action(detail=False, methods=['get'], url_path='match')
    def match(self, request):
        """
        Match authenticated user with appropriate doctors.
        GET /api/doctors/match/
        """
        doctors, is_critical = DoctorMatchingService.match_doctors(request.user)
        
        serializer = DoctorListSerializer(doctors, many=True)
        
        response_data = {
            'status': 'success',
            'is_critical': is_critical,
            'recommended_doctors': serializer.data,
        }
        if is_critical:
            response_data['message'] = 'Critical case - limited to top 3 specialists'
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        """
        Get doctor availability slots.
        GET /api/doctors/{id}/availability/
        """
        doctor = self.get_object()
        slots = doctor.availability_slots.filter(is_active=True)
        
        serializer = DoctorAvailabilitySerializer(slots, many=True)
        return Response({
            'doctor_id': doctor.id,
            'doctor_name': f"{doctor.user.firstName} {doctor.user.lastName}",
            'available_slots': serializer.data
        }, status=status.HTTP_200_OK)
