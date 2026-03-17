from rest_framework import serializers
from appointments.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_details = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor',
            'doctor_details',
            'patient',
            'patient_name',
            'date',
            'start_time',
            'end_time',
            'status',
            'meeting_link',
            'notes',
            'rating',
            'feedback',
            'is_upcoming',
            'can_cancel',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'meeting_link']
    
    def get_doctor_details(self, obj):
        return {
            'id': obj.doctor.id,
            'name': f"{obj.doctor.user.firstName} {obj.doctor.user.lastName}",
            'specialization': obj.doctor.specialization.name if obj.doctor.specialization else None,
            'fee': str(obj.doctor.consultation_fee)
        }
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"
    
    def get_is_upcoming(self, obj):
        return obj.is_upcoming()
    
    def get_can_cancel(self, obj):
        return obj.can_be_cancelled()


class CreateAppointmentSerializer(serializers.Serializer):
    """Serializer for creating appointments."""
    doctor_id = serializers.UUIDField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_doctor_id(self, value):
        from doctors.models import Doctor
        try:
            Doctor.objects.get(id=value, is_available=True, is_verified=True)
            return value
        except Doctor.DoesNotExist:
            raise serializers.ValidationError('Doctor not found or unavailable')
    
    def validate_date(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError('Cannot book appointment in the past')
        return value


class AppointmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing appointments."""
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'doctor_name', 'patient_name', 'date', 'start_time', 'status']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.firstName} {obj.doctor.user.lastName}"
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"


class AppointmentFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for appointment feedback."""
    class Meta:
        model = Appointment
        fields = ['rating', 'feedback']
    
    def validate_rating(self, value):
        if value and (value < 1 or value > 5):
            raise serializers.ValidationError('Rating must be between 1 and 5')
        return value
