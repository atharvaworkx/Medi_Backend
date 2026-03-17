from django.db import models
from django.utils.translation import gettext_lazy as _
from appointments.models import Appointment
from doctors.models import Doctor
from users.models import Users


class Prescription(models.Model):
    """Doctor prescription for patient."""
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    appointment = models.OneToOneField(
        Appointment,
        verbose_name=_('Appointment'),
        on_delete=models.CASCADE,
        related_name='prescription',
        db_column='appointment_id'
    )
    doctor = models.ForeignKey(
        Doctor,
        verbose_name=_('Doctor'),
        on_delete=models.CASCADE,
        related_name='prescriptions',
        db_column='doctor_id'
    )
    patient = models.ForeignKey(
        Users,
        verbose_name=_('Patient'),
        on_delete=models.CASCADE,
        related_name='prescriptions',
        db_column='patient_id'
    )
    medicines = models.JSONField(
        verbose_name=_('Medicines'),
        default=list,
        null=True,
        db_column='medicines'
    )
    lifestyle_recommendations = models.TextField(
        verbose_name=_('Lifestyle Recommendations'),
        null=True,
        db_column='lifestyle_recommendations'
    )
    dietary_recommendations = models.TextField(
        verbose_name=_('Dietary Recommendations'),
        null=True,
        db_column='dietary_recommendations'
    )
    notes = models.TextField(
        verbose_name=_('Doctor Notes'),
        null=True,
        db_column='notes'
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_column='status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'prescriptions'
        verbose_name_plural = 'Prescriptions'
        managed = True
        indexes = [
            models.Index(fields=['appointment']),
            models.Index(fields=['doctor']),
            models.Index(fields=['patient']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Prescription for {self.patient.firstName} - {self.appointment.date}"
    
    def can_edit(self) -> bool:
        """Check if prescription can be edited."""
        return self.status in ['draft', 'active'] and self.appointment.status != 'completed'
    
    def lock_prescription(self):
        """Lock prescription after appointment completion."""
        if self.appointment.status == 'completed':
            self.status = 'completed'
            self.save()
