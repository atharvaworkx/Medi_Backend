from rest_framework import serializers
from consultations.models import ConsultationSession


class ConsultationSessionSerializer(serializers.ModelSerializer):
    """Serializer for consultation sessions."""
    
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultationSession
        fields = [
            'id',
            'appointment',
            'doctor_name',
            'patient_name',
            'appointment_date',
            'appointment_time',
            'status',
            'meeting_link',
            'video_provider',
            'started_at',
            'ended_at',
            'duration_minutes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'meeting_link']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.appointment.doctor.user.firstName} {obj.appointment.doctor.user.lastName}"
    
    def get_patient_name(self, obj):
        return f"{obj.appointment.patient.firstName} {obj.appointment.patient.lastName}"
    
    def get_appointment_date(self, obj):
        return str(obj.appointment.date)
    
    def get_appointment_time(self, obj):
        return str(obj.appointment.start_time)


class ConsultationStartSerializer(serializers.Serializer):
    """Serializer for starting a consultation."""
    appointment_id = serializers.IntegerField()
    
    def validate_appointment_id(self, value):
        from appointments.models import Appointment
        try:
            appointment = Appointment.objects.get(id=value)
            if appointment.status not in ['confirmed', 'booked']:
                raise serializers.ValidationError('Appointment is not available for consultation')
            return value
        except Appointment.DoesNotExist:
            raise serializers.ValidationError('Appointment not found')
