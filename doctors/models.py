from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import Users
from atomicloops.models import AtomicBaseModel


class Specialization(AtomicBaseModel):
    """Doctor specialization based on Ayurvedic principles."""
    
    CATEGORY_CHOICES = (
        ('preventive', _('Preventive Care')),
        ('critical', _('Critical Care')),
        ('specialized', _('Specialized Treatment')),
    )
    
    DOSHA_CHOICES = (
        ('vata', _('Vata')),
        ('pitta', _('Pitta')),
        ('kapha', _('Kapha')),
        ('general', _('General')),
    )
    
    name = models.CharField(
        verbose_name=_('Specialization Name'),
        max_length=200,
        unique=True,
        db_column='name'
    )
    description = models.TextField(
        verbose_name=_('Description'),
        db_column='description',
        null=True
    )
    related_dosha = models.CharField(
        verbose_name=_('Related Dosha'),
        max_length=20,
        choices=DOSHA_CHOICES,
        db_column='related_dosha',
        default='general'
    )
    category = models.CharField(
        verbose_name=_('Category'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        db_column='category'
    )
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )
    
    class Meta:
        db_table = 'specializations'
        verbose_name_plural = 'Specializations'
        managed = True
        indexes = [
            models.Index(fields=['related_dosha']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name


class Doctor(AtomicBaseModel):
    """Doctor profile linked to User."""
    
    user = models.OneToOneField(
        Users,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        db_column='user_id'
    )
    specialization = models.ForeignKey(
        Specialization,
        verbose_name=_('Specialization'),
        on_delete=models.SET_NULL,
        null=True,
        db_column='specialization_id',
        related_name='doctors'
    )
    years_of_experience = models.IntegerField(
        verbose_name=_('Years of Experience'),
        validators=[MinValueValidator(0)],
        db_column='years_of_experience',
        default=0
    )
    qualifications = models.TextField(
        verbose_name=_('Qualifications'),
        db_column='qualifications',
        null=True
    )
    bio = models.TextField(
        verbose_name=_('Bio'),
        db_column='bio',
        null=True
    )
    consultation_fee = models.DecimalField(
        verbose_name=_('Consultation Fee'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='consultation_fee',
        default=0
    )
    rating = models.FloatField(
        verbose_name=_('Rating'),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        db_column='rating',
        default=0.0
    )
    total_consultations = models.IntegerField(
        verbose_name=_('Total Consultations'),
        default=0,
        db_column='total_consultations'
    )
    is_available = models.BooleanField(
        verbose_name=_('Is Available'),
        default=True,
        db_column='is_available'
    )
    is_verified = models.BooleanField(
        verbose_name=_('Is Verified'),
        default=False,
        db_column='is_verified'
    )
    
    class Meta:
        db_table = 'doctors'
        verbose_name_plural = 'Doctors'
        managed = True
        indexes = [
            models.Index(fields=['specialization']),
            models.Index(fields=['is_available']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.firstName} {self.user.lastName}"
    
    def get_average_rating(self):
        """Calculate average rating from appointments."""
        from appointments.models import Appointment
        avg = Appointment.objects.filter(
            doctor=self,
            status='completed'
        ).values('rating').aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else 0.0


class DoctorAvailability(AtomicBaseModel):
    """Doctor weekly availability schedule."""
    
    DAY_CHOICES = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    )
    
    doctor = models.ForeignKey(
        Doctor,
        verbose_name=_('Doctor'),
        on_delete=models.CASCADE,
        related_name='availability_slots',
        db_column='doctor_id'
    )
    day_of_week = models.IntegerField(
        verbose_name=_('Day of Week'),
        choices=DAY_CHOICES,
        db_column='day_of_week'
    )
    start_time = models.TimeField(
        verbose_name=_('Start Time'),
        db_column='start_time'
    )
    end_time = models.TimeField(
        verbose_name=_('End Time'),
        db_column='end_time'
    )
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )
    
    class Meta:
        db_table = 'doctor_availability'
        verbose_name_plural = 'Doctor Availability'
        managed = True
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')
        indexes = [
            models.Index(fields=['doctor', 'day_of_week']),
        ]
    
    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()}"
