from django.db import models
from django.utils.translation import gettext_lazy as _
from appointments.models import Appointment
from doctors.models import Doctor
from users.models import Users


class ConsultationSession(models.Model):
    """Tracks online consultation sessions."""
    
    STATUS_CHOICES = (
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    appointment = models.OneToOneField(
        Appointment,
        verbose_name=_('Appointment'),
        on_delete=models.CASCADE,
        related_name='consultation_session',
        db_column='appointment_id'
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        db_column='status'
    )
    meeting_link = models.URLField(
        verbose_name=_('Meeting Link'),
        max_length=500,
        null=True,
        db_column='meeting_link'
    )
    video_provider = models.CharField(
        verbose_name=_('Video Provider'),
        max_length=50,
        default='mock',
        db_column='video_provider'
    )
    provider_meeting_id = models.CharField(
        verbose_name=_('Provider Meeting ID'),
        max_length=255,
        null=True,
        db_column='provider_meeting_id'
    )
    started_at = models.DateTimeField(
        verbose_name=_('Started At'),
        null=True,
        db_column='started_at'
    )
    ended_at = models.DateTimeField(
        verbose_name=_('Ended At'),
        null=True,
        db_column='ended_at'
    )
    duration_minutes = models.IntegerField(
        verbose_name=_('Duration (minutes)'),
        null=True,
        db_column='duration_minutes'
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
        db_table = 'consultation_sessions'
        verbose_name_plural = 'Consultation Sessions'
        managed = True
        indexes = [
            models.Index(fields=['appointment']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Consultation {self.appointment.id} - {self.status}"
