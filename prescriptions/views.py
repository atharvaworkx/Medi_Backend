from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from prescriptions.models import Prescription
from prescriptions.serializers import PrescriptionSerializer, PrescriptionCreateUpdateSerializer
from appointments.models import Appointment


class PrescriptionViewSet(viewsets.ModelViewSet):
    """Manage prescriptions."""
    
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter prescriptions by user role."""
        user = self.request.user
        
        if hasattr(user, 'doctor_profile'):
            return Prescription.objects.filter(
                doctor=user.doctor_profile
            ).select_related('appointment', 'doctor', 'patient')
        
        return Prescription.objects.filter(
            patient=user
        ).select_related('appointment', 'doctor', 'patient')
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_prescription(self, request):
        """
        Create a prescription for an appointment.
        POST /api/prescriptions/create/
        """
        serializer = PrescriptionCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        appointment = Appointment.objects.get(id=serializer.validated_data['appointment_id'])
        
        # Only doctor can create prescription
        if not hasattr(request.user, 'doctor_profile') or appointment.doctor.user != request.user:
            return Response(
                {'error': 'Only assigned doctor can create prescription'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if prescription already exists
        if hasattr(appointment, 'prescription'):
            return Response(
                {'error': 'Prescription already exists for this appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescription = Prescription.objects.create(
            appointment=appointment,
            doctor=request.user.doctor_profile,
            patient=appointment.patient,
            medicines=serializer.validated_data.get('medicines', []),
            lifestyle_recommendations=serializer.validated_data.get('lifestyle_recommendations', ''),
            dietary_recommendations=serializer.validated_data.get('dietary_recommendations', ''),
            notes=serializer.validated_data.get('notes', ''),
            status='active'
        )
        
        return Response(
            {
                'status': 'success',
                'prescription_id': prescription.id
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def update_prescription(self, request, pk=None):
        """
        Update prescription.
        PATCH /api/prescriptions/{id}/update_prescription/
        """
        prescription = self.get_object()
        
        # Only doctor can update
        if not hasattr(request.user, 'doctor_profile') or prescription.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if editable
        if not prescription.can_edit():
            return Response(
                {'error': 'Prescription cannot be edited after appointment is completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PrescriptionCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update fields
        if 'medicines' in serializer.validated_data:
            prescription.medicines = serializer.validated_data['medicines']
        if 'lifestyle_recommendations' in serializer.validated_data:
            prescription.lifestyle_recommendations = serializer.validated_data['lifestyle_recommendations']
        if 'dietary_recommendations' in serializer.validated_data:
            prescription.dietary_recommendations = serializer.validated_data['dietary_recommendations']
        if 'notes' in serializer.validated_data:
            prescription.notes = serializer.validated_data['notes']
        
        prescription.save()
        
        return Response(
            PrescriptionSerializer(prescription).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """
        Get prescription details.
        GET /api/prescriptions/{id}/details/
        """
        prescription = self.get_object()
        
        # Verify access
        if prescription.patient != request.user and prescription.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_200_OK)
