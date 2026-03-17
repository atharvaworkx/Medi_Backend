from rest_framework import serializers
from doctors.models import Doctor, Specialization, DoctorAvailability


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'related_dosha', 'category', 'description']


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )
    
    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time', 'is_active']


class DoctorListSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id',
            'user_name',
            'specialization',
            'years_of_experience',
            'rating',
            'consultation_fee',
            'is_available',
            'total_consultations'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"


class DoctorDetailSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()
    availability_slots = DoctorAvailabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id',
            'user_name',
            'specialization',
            'years_of_experience',
            'qualifications',
            'bio',
            'rating',
            'consultation_fee',
            'is_available',
            'is_verified',
            'total_consultations',
            'availability_slots'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"


class DoctorMatchingResponseSerializer(serializers.Serializer):
    """Response format for doctor matching."""
    status = serializers.CharField()
    is_critical = serializers.BooleanField()
    recommended_doctors = DoctorListSerializer(many=True)
    message = serializers.CharField(required=False, allow_blank=True)
