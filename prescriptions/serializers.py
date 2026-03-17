from rest_framework import serializers
from prescriptions.models import Prescription


class MedicineItemSerializer(serializers.Serializer):
    """Serializer for individual medicine items."""
    
    name = serializers.CharField(max_length=200)
    dosage = serializers.CharField(max_length=200)
    frequency = serializers.CharField(max_length=100)
    duration = serializers.CharField(max_length=100)
    notes = serializers.CharField(required=False, allow_blank=True)


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for prescriptions."""
    
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id',
            'appointment',
            'doctor',
            'doctor_name',
            'patient',
            'patient_name',
            'appointment_date',
            'medicines',
            'lifestyle_recommendations',
            'dietary_recommendations',
            'notes',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'doctor', 'patient']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.firstName} {obj.doctor.user.lastName}"
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"
    
    def get_appointment_date(self, obj):
        return str(obj.appointment.date)


class PrescriptionCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating prescriptions."""
    
    appointment_id = serializers.IntegerField()
    medicines = MedicineItemSerializer(many=True, required=False)
    lifestyle_recommendations = serializers.CharField(required=False, allow_blank=True)
    dietary_recommendations = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_appointment_id(self, value):
        from appointments.models import Appointment
        try:
            appointment = Appointment.objects.get(id=value)
            return value
        except Appointment.DoesNotExist:
            raise serializers.ValidationError('Appointment not found')
