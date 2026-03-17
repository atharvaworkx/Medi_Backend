from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from consultations.models import ConsultationSession
from consultations.serializers import ConsultationSessionSerializer, ConsultationStartSerializer
from consultations.services.video_service import VideoServiceFactory
from appointments.models import Appointment
from datetime import datetime


class ConsultationSessionViewSet(viewsets.ModelViewSet):
    """Manage consultation sessions."""
    
    serializer_class = ConsultationSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter consultations by user role."""
        user = self.request.user
        
        if hasattr(user, 'doctor_profile'):
            return ConsultationSession.objects.filter(
                appointment__doctor=user.doctor_profile
            ).select_related('appointment__doctor', 'appointment__patient')
        
        return ConsultationSession.objects.filter(
            appointment__patient=user
        ).select_related('appointment__doctor', 'appointment__patient')
    
    @action(detail=False, methods=['post'], url_path='start')
    def start_consultation(self, request):
        """
        Start a consultation session.
        POST /api/consultations/start/
        """
        serializer = ConsultationStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        appointment = Appointment.objects.get(id=serializer.validated_data['appointment_id'])
        
        # Verify access
        if appointment.patient != request.user and appointment.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if session already exists
        session, created = ConsultationSession.objects.get_or_create(
            appointment=appointment,
            defaults={
                'status': 'in_progress',
                'started_at': datetime.now(),
                'video_provider': 'mock'
            }
        )
        
        if created:
            # Generate meeting link
            provider = VideoServiceFactory.get_provider()
            meeting_details = provider.create_meeting(
                appointment.id,
                f"{appointment.doctor.user.firstName} {appointment.doctor.user.lastName}",
                f"{appointment.patient.firstName} {appointment.patient.lastName}"
            )
            
            session.meeting_link = meeting_details['meeting_link']
            session.provider_meeting_id = meeting_details['provider_meeting_id']
            session.save()
        
        serializer = ConsultationSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def end_consultation(self, request, pk=None):
        """
        End a consultation session.
        POST /api/consultations/{id}/end_consultation/
        """
        session = self.get_object()
        
        # Verify access
        if session.appointment.patient != request.user and session.appointment.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if session.status == 'completed':
            return Response(
                {'error': 'Consultation already ended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'completed'
        session.ended_at = datetime.now()
        
        if session.started_at:
            duration = (session.ended_at - session.started_at).total_seconds() / 60
            session.duration_minutes = int(duration)
        
        session.save()
        
        # Update appointment status
        session.appointment.status = 'completed'
        session.appointment.save()
        
        serializer = ConsultationSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """
        Get consultation details with meeting link.
        GET /api/consultations/{id}/details/
        """
        session = self.get_object()
        
        # Verify access
        if session.appointment.patient != request.user and session.appointment.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ConsultationSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
