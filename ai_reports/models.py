from django.db import models
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from users.models import Users


class HealthAssessmentReport(AtomicBaseModel):
    userId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='healthAssessmentReport',
        db_column='user_id',
        verbose_name=_('User')
    )
    prakritResult = models.JSONField(
        verbose_name=_('Prakriti Result'),
        default=dict,
        db_column='prakriti_result',
        help_text='{vata: %, pitta: %, kapha: %}'
    )
    vikritResult = models.JSONField(
        verbose_name=_('Vikriti Result'),
        default=dict,
        db_column='vikriti_result',
        help_text='{vata: %, pitta: %, kapha: %}'
    )
    digestiveRisk = models.JSONField(
        verbose_name=_('Digestive Risk'),
        default=dict,
        db_column='digestive_risk',
        help_text='{"risk_level": "low/medium/high", "details": []}'
    )
    skinRisk = models.JSONField(
        verbose_name=_('Skin Risk'),
        default=dict,
        db_column='skin_risk',
        help_text='{"risk_level": "low/medium/high", "details": []}'
    )
    mentalHealthRisk = models.JSONField(
        verbose_name=_('Mental Health Risk'),
        default=dict,
        db_column='mental_health_risk',
        help_text='{"risk_level": "low/medium/high", "details": []}'
    )
    imageAnalysisResults = models.JSONField(
        verbose_name=_('Image Analysis Results'),
        default=dict,
        db_column='image_analysis_results',
        help_text='Aggregated analysis from all uploaded images'
    )
    overallSummary = models.TextField(
        verbose_name=_('Overall Summary'),
        db_column='overall_summary'
    )
    recommendations = models.JSONField(
        verbose_name=_('Recommendations'),
        default=list,
        db_column='recommendations',
        help_text='List of recommendations'
    )
    riskFlags = models.JSONField(
        verbose_name=_('Risk Flags'),
        default=list,
        db_column='risk_flags',
        help_text='Critical issues to address'
    )
    isCritical = models.BooleanField(
        verbose_name=_('Is Critical'),
        default=False,
        db_column='is_critical'
    )
    overallScore = models.IntegerField(
        verbose_name=_('Overall Score'),
        default=0,
        db_column='overall_score'
    )
    healthScores = models.JSONField(
        verbose_name=_('Health Scores'),
        default=dict,
        db_column='health_scores',
        help_text='{Digestion: %, Immunity: %, Sleep: %, Stress: %, Energy: %}'
    )
    lastGeneratedAt = models.DateTimeField(
        verbose_name=_('Last Generated At'),
        auto_now_add=True,
        db_column='last_generated_at'
    )

    class Meta:
        db_table = 'health_assessment_reports'
        verbose_name_plural = 'health_assessment_reports'
        managed = True

    def __str__(self):
        return f"Health Report - {self.userId.email}"
