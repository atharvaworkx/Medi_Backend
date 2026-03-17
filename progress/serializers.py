from rest_framework import serializers
from progress.models import (
    DailyHealthLog,
    Symptom,
    SymptomLog,
    FollowUpRecommendation
)


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'category', 'related_dosha', 'description']


class SymptomLogSerializer(serializers.ModelSerializer):
    symptom_details = SymptomSerializer(source='symptom', read_only=True)
    
    class Meta:
        model = SymptomLog
        fields = ['id', 'symptom', 'symptom_details', 'severity', 'notes']


class DailyHealthLogSerializer(serializers.ModelSerializer):
    symptom_logs = SymptomLogSerializer(many=True, read_only=True)
    overall_score = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyHealthLog
        fields = [
            'id',
            'date',
            'energy_level',
            'digestion_quality',
            'stress_level',
            'sleep_hours',
            'diet_notes',
            'symptom_notes',
            'bowel_pattern',
            'exercise_notes',
            'mood_notes',
            'symptom_logs',
            'overall_score',
            'created_at'
        ]
    
    def get_overall_score(self, obj):
        return obj.get_overall_score()


class CreateDailyHealthLogSerializer(serializers.Serializer):
    """Serializer for creating daily health logs."""
    date = serializers.DateField()
    energy_level = serializers.IntegerField(min_value=1, max_value=10)
    digestion_quality = serializers.IntegerField(min_value=1, max_value=10)
    stress_level = serializers.IntegerField(min_value=1, max_value=10)
    sleep_hours = serializers.FloatField(min_value=0, max_value=24)
    diet_notes = serializers.CharField(required=False, allow_blank=True)
    symptom_notes = serializers.CharField(required=False, allow_blank=True)
    bowel_pattern = serializers.CharField(required=False, allow_blank=True)
    exercise_notes = serializers.CharField(required=False, allow_blank=True)
    mood_notes = serializers.CharField(required=False, allow_blank=True)
    symptoms = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )


class FollowUpRecommendationSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FollowUpRecommendation
        fields = [
            'id',
            'suggested_date',
            'priority',
            'reason',
            'description',
            'is_booked',
            'doctor_name',
            'created_at'
        ]
    
    def get_doctor_name(self, obj):
        if obj.recommended_doctor:
            return f"Dr. {obj.recommended_doctor.user.firstName} {obj.recommended_doctor.user.lastName}"
        return None


class ProgressAnalyticsSerializer(serializers.Serializer):
    """Response format for progress analytics."""
    period = serializers.CharField()
    trend_summary = serializers.CharField()
    improvement_score = serializers.IntegerField()
    risk_flags = serializers.ListField(child=serializers.CharField())
    recommended_action = serializers.CharField()
    stats = serializers.DictField()
