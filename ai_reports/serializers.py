from rest_framework import serializers
from atomicloops.serializers import AtomicSerializer
from ai_reports.models import HealthAssessmentReport


class HealthAssessmentReportSerializer(AtomicSerializer):
    dominantPrakriti = serializers.SerializerMethodField()
    dominantVikriti = serializers.SerializerMethodField()

    class Meta:
        model = HealthAssessmentReport
        fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'prakritResult', 'vikritResult',
            'dominantPrakriti', 'dominantVikriti', 'digestiveRisk', 'skinRisk', 'mentalHealthRisk',
            'imageAnalysisResults', 'overallSummary', 'recommendations', 'riskFlags', 'isCritical', 
            'overallScore', 'healthScores', 'lastGeneratedAt'
        ]
        get_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'prakritResult', 'vikritResult',
            'dominantPrakriti', 'dominantVikriti', 'digestiveRisk', 'skinRisk', 'mentalHealthRisk',
            'imageAnalysisResults', 'overallSummary', 'recommendations', 'riskFlags', 'isCritical', 
            'overallScore', 'healthScores', 'lastGeneratedAt'
        ]
        list_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'dominantPrakriti', 'dominantVikriti', 'isCritical'
        ]
        read_only_fields = ['id', 'userId', 'lastGeneratedAt', 'createdAt', 'updatedAt']

    def get_dominantPrakriti(self, obj):
        prakriti = obj.prakritResult
        return max(prakriti, key=prakriti.get) if prakriti else None

    def get_dominantVikriti(self, obj):
        vikriti = obj.vikritResult
        return max(vikriti, key=vikriti.get) if vikriti else None
