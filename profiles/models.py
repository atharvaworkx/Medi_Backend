from django.db import models
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from users.models import Users


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)


class UserProfile(AtomicBaseModel):
    userId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='profile',
        db_column='user_id',
        verbose_name=_('User')
    )
    fullName = models.CharField(
        verbose_name=_('Full Name'),
        max_length=200,
        db_column='full_name',
        null=True
    )
    age = models.IntegerField(
        verbose_name=_('Age'),
        null=True,
        db_column='age'
    )
    dateOfBirth = models.DateField(
        verbose_name=_('Date of Birth'),
        null=True,
        db_column='date_of_birth'
    )
    gender = models.CharField(
        verbose_name=_('Gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        db_column='gender',
        null=True
    )
    location = models.CharField(
        verbose_name=_('Location'),
        max_length=255,
        db_column='location',
        null=True
    )
    heightCm = models.IntegerField(
        verbose_name=_('Height (cm)'),
        null=True,
        db_column='height_cm'
    )
    weightKg = models.DecimalField(
        verbose_name=_('Weight (kg)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        db_column='weight_kg'
    )
    bloodType = models.CharField(
        verbose_name=_('Blood Type'),
        max_length=10,
        null=True,
        db_column='blood_type'
    )
    bio = models.TextField(
        verbose_name=_('Bio'),
        null=True,
        db_column='bio'
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name_plural = 'user_profiles'
        managed = True

    def __str__(self):
        return f"Profile: {self.userId.email}"
