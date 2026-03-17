from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from users.models import Users
from doctors.models import Doctor
from ai_reports.models import HealthAssessmentReport


class Symptom(AtomicBaseModel):
    """Master list of symptoms for tracking."""
    
    CATEGORY_CHOICES = (
        ('digestive', _('Digestive')),
        ('skin', _('Skin')),
        ('mental', _('Mental Health')),
        ('general', _('General')),
        ('respiratory', _('Respiratory')),
        ('joint', _('Joint & Movement')),
    )
    
    DOSHA_CHOICES = (
        ('vata', _('Vata')),
        ('pitta', _('Pitta')),
        ('kapha', _('Kapha')),
        ('general', _('General')),
    )
    
    name = models.CharField(
        verbose_name=_('Symptom Name'),
        max_length=200,
        unique=True,
        db_column='name'
    )
    category = models.CharField(
        verbose_name=_('Category'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        db_column='category'
    )
    related_dosha = models.CharField(
        verbose_name=_('Related Dosha'),
        max_length=20,
        choices=DOSHA_CHOICES,
        db_column='related_dosha',
        default='general'
    )
    description = models.TextField(
        verbose_name=_('Description'),
        db_column='description',
        null=True
    )
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )
    
    class Meta:
        db_table = 'symptoms'
        verbose_name_plural = 'Symptoms'
        managed = True
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['related_dosha']),
        ]
    
    def __str__(self):
        return self.name


class DailyHealthLog(AtomicBaseModel):
    """Daily health tracking log for patients."""
    
    BOWEL_PATTERN_CHOICES = (
        ('normal', _('Normal')),
        ('constipation', _('Constipation')),
        ('loose', _('Loose')),
        ('irregular', _('Irregular')),
    )
    
    user = models.ForeignKey(
        Users,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='health_logs',
        db_column='user_id'
    )
    date = models.DateField(
        verbose_name=_('Log Date'),
        db_column='log_date'
    )
    energy_level = models.IntegerField(
        verbose_name=_('Energy Level'),
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        db_column='energy_level'
    )
    digestion_quality = models.IntegerField(
        verbose_name=_('Digestion Quality'),
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        db_column='digestion_quality'
    )
    stress_level = models.IntegerField(
        verbose_name=_('Stress Level'),
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        db_column='stress_level'
    )
    sleep_hours = models.FloatField(
        verbose_name=_('Sleep Hours'),
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        db_column='sleep_hours'
    )
    diet_notes = models.TextField(
        verbose_name=_('Diet Notes'),
        db_column='diet_notes',
        null=True
    )
    symptom_notes = models.TextField(
        verbose_name=_('Symptom Notes'),
        db_column='symptom_notes',
        null=True
    )
    bowel_pattern = models.CharField(
        verbose_name=_('Bowel Pattern'),
        max_length=20,
        choices=BOWEL_PATTERN_CHOICES,
        db_column='bowel_pattern',
        null=True
    )
    exercise_notes = models.TextField(
        verbose_name=_('Exercise Notes'),
        db_column='exercise_notes',
        null=True
    )
    mood_notes = models.TextField(
        verbose_name=_('Mood Notes'),
        db_column='mood_notes',
        null=True
    )
    
    class Meta:
        db_table = 'daily_health_logs'
        verbose_name_plural = 'Daily Health Logs'
        managed = True
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['date']),
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.firstName} - {self.date}"
    
    def get_overall_score(self) -> float:
        """Calculate overall health score for the day."""
        return round((
            self.energy_level * 0.25 +
            self.digestion_quality * 0.25 +
            (10 - self.stress_level) * 0.25 +
            (min(self.sleep_hours, 8) / 8 * 10) * 0.25
        ), 2)


class SymptomLog(AtomicBaseModel):
    """Log of symptoms reported on a specific day."""
    
    daily_log = models.ForeignKey(
        DailyHealthLog,
        verbose_name=_('Daily Log'),
        on_delete=models.CASCADE,
        related_name='symptom_logs',
        db_column='daily_log_id'
    )
    symptom = models.ForeignKey(
        Symptom,
        verbose_name=_('Symptom'),
        on_delete=models.CASCADE,
        related_name='logs',
        db_column='symptom_id'
    )
    severity = models.IntegerField(
        verbose_name=_('Severity (1-5)'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_column='severity'
    )
    notes = models.TextField(
        verbose_name=_('Notes'),
        db_column='notes',
        null=True
    )
    
    class Meta:
        db_table = 'symptom_logs'
        verbose_name_plural = 'Symptom Logs'
        managed = True
        unique_together = ('daily_log', 'symptom')
        indexes = [
            models.Index(fields=['daily_log']),
            models.Index(fields=['symptom']),
        ]
    
    def __str__(self):
        return f"{self.symptom.name} - Severity {self.severity}"


class FollowUpRecommendation(AtomicBaseModel):
    """Auto-generated follow-up recommendations."""
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    )
    
    REASON_CHOICES = (
        ('trend', _('Symptom Trend')),
        ('no_improvement', _('No Improvement After Prescription')),
        ('high_stress', _('Prolonged High Stress')),
        ('doctor_recommended', _('Doctor Recommended')),
        ('severe_symptoms', _('Severe Symptoms Detected')),
        ('routine_checkup', _('Routine Follow-up')),
    )
    
    user = models.ForeignKey(
        Users,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='followup_recommendations',
        db_column='user_id'
    )
    ai_report = models.ForeignKey(
        HealthAssessmentReport,
        verbose_name=_('Related AI Report'),
        on_delete=models.SET_NULL,
        null=True,
        db_column='ai_report_id',
        related_name='followup_recommendations'
    )
    recommended_doctor = models.ForeignKey(
        Doctor,
        verbose_name=_('Recommended Doctor'),
        on_delete=models.SET_NULL,
        null=True,
        db_column='recommended_doctor_id',
        related_name='followup_recommendations'
    )
    suggested_date = models.DateField(
        verbose_name=_('Suggested Follow-up Date'),
        db_column='suggested_date'
    )
    priority = models.CharField(
        verbose_name=_('Priority'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        db_column='priority'
    )
    reason = models.CharField(
        verbose_name=_('Reason'),
        max_length=50,
        choices=REASON_CHOICES,
        db_column='reason'
    )
    description = models.TextField(
        verbose_name=_('Description'),
        db_column='description',
        null=True
    )
    is_booked = models.BooleanField(
        verbose_name=_('Is Booked'),
        default=False,
        db_column='is_booked'
    )
    related_appointment = models.OneToOneField(
        'appointments.Appointment',
        verbose_name=_('Related Appointment'),
        on_delete=models.SET_NULL,
        null=True,
        db_column='related_appointment_id',
        related_name='followup_recommendation'
    )
    
    class Meta:
        db_table = 'followup_recommendations'
        verbose_name_plural = 'Follow-up Recommendations'
        managed = True
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['priority']),
            models.Index(fields=['suggested_date']),
            models.Index(fields=['is_booked']),
        ]
    
    def __str__(self):
        return f"Follow-up for {self.user.firstName} - {self.priority.upper()}"
