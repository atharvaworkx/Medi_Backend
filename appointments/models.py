from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from users.models import Users
from doctors.models import Doctor
from datetime import datetime, timedelta


class Appointment(models.Model):
    """Appointment model for patient-doctor consultations."""
    
    STATUS_CHOICES = (
        ('booked', _('Booked')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no-show', _('No Show')),
    )
    
    patient = models.ForeignKey(
        Users,
        verbose_name=_('Patient'),
        on_delete=models.CASCADE,
        related_name='appointments_as_patient',
        db_column='patient_id'
    )
    doctor = models.ForeignKey(
        Doctor,
        verbose_name=_('Doctor'),
        on_delete=models.CASCADE,
        related_name='appointments',
        db_column='doctor_id'
    )
    date = models.DateField(
        verbose_name=_('Appointment Date'),
        db_column='appointment_date'
    )
    start_time = models.TimeField(
        verbose_name=_('Start Time'),
        db_column='start_time'
    )
    end_time = models.TimeField(
        verbose_name=_('End Time'),
        db_column='end_time'
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='booked',
        db_column='status'
    )
    meeting_link = models.URLField(
        verbose_name=_('Meeting Link'),
        db_column='meeting_link',
        null=True,
        max_length=500
    )
    notes = models.TextField(
        verbose_name=_('Notes'),
        db_column='notes',
        null=True
    )
    cancellation_reason = models.TextField(
        verbose_name=_('Cancellation Reason'),
        db_column='cancellation_reason',
        null=True
    )
    rating = models.IntegerField(
        verbose_name=_('Rating'),
        db_column='rating',
        null=True
    )
    feedback = models.TextField(
        verbose_name=_('Feedback'),
        db_column='feedback',
        null=True
    )
    is_followup = models.BooleanField(
        verbose_name=_('Is Follow-up'),
        default=False,
        db_column='is_followup'
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
        db_table = 'appointments'
        verbose_name_plural = 'Appointments'
        managed = True
        unique_together = ('doctor', 'date', 'start_time')
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['doctor']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['patient', 'date']),
            models.Index(fields=['doctor', 'date']),
        ]
    
    def __str__(self):
        return f"{self.patient.firstName} - Dr. {self.doctor.user.firstName} ({self.date})"
    
    def clean(self):
        """Validate appointment."""
        # NOTE: date-in-past check disabled for dev; re-enable in prod
        # from datetime import date as date_obj
        # if self.date < date_obj.today():
        #     raise ValidationError(_('Cannot book appointment in the past'))

        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError(_('End time must be after start time'))

    def save(self, *args, **kwargs):
        # NOTE: full_clean disabled for dev to avoid clean() blocking admin
        # self.full_clean()
        super().save(*args, **kwargs)
    
    def is_upcoming(self):
        """Check if appointment is upcoming."""
        appointment_datetime = datetime.combine(self.date, self.start_time)
        return appointment_datetime > datetime.now()
    
    def can_be_cancelled(self):
        """Check if appointment can be cancelled (at least 24 hours before)."""
        appointment_datetime = datetime.combine(self.date, self.start_time)
        hours_until = (appointment_datetime - datetime.now()).total_seconds() / 3600
        return hours_until >= 24 and self.status in ['booked', 'confirmed']
