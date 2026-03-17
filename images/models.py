from django.db import models
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from users.models import Users


IMAGE_TYPE_CHOICES = (
    ('iris', 'Iris'),
    ('tongue', 'Tongue'),
    ('hair', 'Hair'),
    ('skin', 'Skin'),
)

PROCESSING_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
)


class HealthImage(AtomicBaseModel):
    userId = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='healthImages',
        db_column='user_id',
        verbose_name=_('User')
    )
    imageType = models.CharField(
        verbose_name=_('Image Type'),
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        db_column='image_type'
    )
    imageUrl = models.URLField(
        verbose_name=_('Image URL'),
        max_length=512,
        db_column='image_url'
    )
    s3Key = models.CharField(
        verbose_name=_('S3 Key'),
        max_length=512,
        db_column='s3_key',
        null=True
    )
    fileSize = models.IntegerField(
        verbose_name=_('File Size (bytes)'),
        db_column='file_size',
        null=True
    )
    uploadedAt = models.DateTimeField(
        verbose_name=_('Uploaded At'),
        auto_now_add=True,
        db_column='uploaded_at'
    )
    aiProcessed = models.BooleanField(
        verbose_name=_('AI Processed'),
        default=False,
        db_column='ai_processed'
    )
    aiResults = models.JSONField(
        verbose_name=_('AI Results'),
        null=True,
        db_column='ai_results',
        help_text='Storage for AI analysis results'
    )
    processingStatus = models.CharField(
        verbose_name=_('Processing Status'),
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending',
        db_column='processing_status'
    )

    class Meta:
        db_table = 'health_images'
        verbose_name_plural = 'health_images'
        managed = True
        indexes = [
            models.Index(fields=['userId', 'imageType']),
            models.Index(fields=['aiProcessed']),
        ]

    def __str__(self):
        return f"{self.get_imageType_display()} - {self.userId.email}"
