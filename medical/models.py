from django.db import models
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from users.models import Users


class MedicalHistory(AtomicBaseModel):
    userId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='medicalHistory',
        db_column='user_id',
        verbose_name=_('User')
    )
    existingConditions = models.JSONField(
        verbose_name=_('Existing Conditions'),
        default=list,
        db_column='existing_conditions',
        help_text='List of existing medical conditions'
    )
    ongoingTreatments = models.JSONField(
        verbose_name=_('Ongoing Treatments'),
        default=list,
        db_column='ongoing_treatments',
        help_text='Current treatments'
    )
    allergies = models.JSONField(
        verbose_name=_('Allergies'),
        default=list,
        db_column='allergies',
        help_text='Known allergies'
    )
    familyMedicalHistory = models.JSONField(
        verbose_name=_('Family Medical History'),
        default=dict,
        db_column='family_medical_history',
        help_text='Family medical conditions'
    )
    medications = models.JSONField(
        verbose_name=_('Current Medications'),
        default=list,
        db_column='medications',
        help_text='Current medications'
    )
    lifestyleNotes = models.TextField(
        verbose_name=_('Lifestyle Notes'),
        null=True,
        db_column='lifestyle_notes',
        help_text='Diet, exercise, sleep patterns, etc.'
    )
    version = models.IntegerField(
        verbose_name=_('Version'),
        default=1,
        db_column='version'
    )
    isActive = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )

    class Meta:
        db_table = 'medical_history'
        verbose_name_plural = 'medical_history'
        managed = True

    def __str__(self):
        return f"Medical History: {self.userId.email} (v{self.version})"


class MedicalHistoryVersion(AtomicBaseModel):
    userId = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='medicalHistoryVersions',
        db_column='user_id',
        verbose_name=_('User')
    )
    versionData = models.JSONField(
        verbose_name=_('Version Data'),
        db_column='version_data'
    )
    versionNumber = models.IntegerField(
        verbose_name=_('Version Number'),
        db_column='version_number'
    )

    class Meta:
        db_table = 'medical_history_versions'
        verbose_name_plural = 'medical_history_versions'
        managed = True
        ordering = ['-versionNumber']

    def __str__(self):
        return f"Medical History v{self.versionNumber} - {self.userId.email}"
