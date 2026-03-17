from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from appointments.models import Appointment
from appointments.serializers import (
    AppointmentSerializer,
    CreateAppointmentSerializer,
    AppointmentListSerializer,
    AppointmentFeedbackSerializer
)
from appointments.services.appointment_service import AppointmentService
from doctors.models import Doctor


class AppointmentViewSet(viewsets.ModelViewSet):
    """Appointment management."""
    
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user role."""
        user = self.request.user
        
        if hasattr(user, 'doctor_profile'):
            return Appointment.objects.filter(
                doctor=user.doctor_profile
            ).select_related('doctor__user', 'doctor__specialization', 'patient').order_by('-date')
        
        return Appointment.objects.filter(
            patient=user
        ).select_related('doctor__user', 'doctor__specialization', 'patient').order_by('-date')
    
    def list(self, request, *args, **kwargs):
        """List appointments with pagination."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = AppointmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AppointmentListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='book')
    def book_appointment(self, request):
        """
        Book new appointment.
        POST /api/appointments/book/
        """
        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        appointment, response = AppointmentService.book_appointment(
            patient=request.user,
            doctor_id=serializer.validated_data['doctor_id'],
            date=serializer.validated_data['date'],
            start_time=serializer.validated_data['start_time'],
            notes=serializer.validated_data.get('notes', '')
        )
        
        if appointment:
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel appointment."""
        appointment = self.get_object()
        
        if appointment.patient != request.user and not hasattr(request.user, 'doctor_profile'):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', '')
        response = AppointmentService.cancel_appointment(appointment, reason)
        
        return Response(
            response,
            status=status.HTTP_200_OK if response['status'] == 'success' else status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Submit appointment feedback."""
        appointment = self.get_object()
        
        if appointment.patient != request.user:
            return Response(
                {'error': 'Only patient can provide feedback'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status != 'completed':
            return Response(
                {'error': 'Can only rate completed appointments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AppointmentFeedbackSerializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'status': 'success', 'message': 'Feedback saved'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='my')
    def my_appointments(self, request):
        """Get user's appointments."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='doctor')
    def doctor_appointments(self, request):
        """Get doctor's appointments (doctor only)."""
        if not hasattr(request.user, 'doctor_profile'):
            return Response(
                {'error': 'Only doctors can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = Appointment.objects.filter(
            doctor=request.user.doctor_profile
        ).select_related('patient', 'doctor__user', 'doctor__specialization').order_by('-date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AppointmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AppointmentListSerializer(queryset, many=True)
        return Response(serializer.data)


class DoctorAvailabilityViewSet(viewsets.ViewSet):
    """Get available appointment slots for a doctor."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def slots(self, request):
        """Get available slots for a doctor."""
        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')
        
        if not doctor_id or not date_str:
            return Response(
                {'error': 'doctor_id and date parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            doctor = Doctor.objects.get(id=doctor_id)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            slots = AppointmentService.get_available_slots(doctor, date)
            
            return Response({
                'doctor_id': doctor_id,
                'date': date_str,
                'slots': slots
            }, status=status.HTTP_200_OK)
        
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
