from django.db import models
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from appointments.models import Appointment
from users.models import Users


class ChatSession(AtomicBaseModel):
    """Global AI chat session across platform."""
    
    CONTEXT_TYPE_CHOICES = (
        ('general', _('General Health Question')),
        ('consultation', _('Consultation Related')),
        ('followup', _('Follow-up Discussion')),
        ('report_discussion', _('Report Discussion')),
        ('prescription', _('Prescription Clarification')),
        ('lifestyle', _('Lifestyle & Diet')),
    )
    
    user = models.ForeignKey(
        Users,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        db_column='user_id'
    )
    context_type = models.CharField(
        verbose_name=_('Context Type'),
        max_length=30,
        choices=CONTEXT_TYPE_CHOICES,
        default='general',
        db_column='context_type'
    )
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )
    title = models.CharField(
        verbose_name=_('Session Title'),
        max_length=255,
        db_column='title',
        null=True
    )
    message_count = models.IntegerField(
        verbose_name=_('Message Count'),
        default=0,
        db_column='message_count'
    )
    
    class Meta:
        db_table = 'chat_sessions'
        verbose_name_plural = 'Chat Sessions'
        managed = True
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Chat - {self.user.firstName} ({self.context_type})"


class ChatMessage(AtomicBaseModel):
    """Store conversation messages - supports both consultation and global chat."""
    
    SENDER_CHOICES = (
        ('patient', _('Patient')),
        ('doctor', _('Doctor')),
        ('ai', _('AI Assistant')),
        ('user', _('User')),
        ('assistant', _('Assistant')),
    )
    
    MESSAGE_TYPE_CHOICES = (
        ('user', _('User Message')),
        ('assistant', _('Assistant Response')),
        ('system', _('System Message')),
    )
    
    # Legacy appointment-based chat (nullable for backward compatibility)
    appointment = models.ForeignKey(
        Appointment,
        verbose_name=_('Appointment'),
        on_delete=models.CASCADE,
        related_name='chat_messages',
        db_column='appointment_id',
        null=True
    )
    
    # New global session-based chat
    session = models.ForeignKey(
        ChatSession,
        verbose_name=_('Chat Session'),
        on_delete=models.CASCADE,
        related_name='messages',
        db_column='session_id',
        null=True
    )
    
    
    # Support both old and new message formats
    sender = models.CharField(
        verbose_name=_('Sender'),
        max_length=20,
        choices=SENDER_CHOICES,
        db_column='sender',
        null=True
    )
    
    message_type = models.CharField(
        verbose_name=_('Message Type'),
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        db_column='message_type',
        null=True
    )
    
    message = models.TextField(
        verbose_name=_('Message'),
        db_column='message',
        null=True
    )
    
    content = models.TextField(
        verbose_name=_('Message Content'),
        db_column='content',
        null=True
    )
    
    intent = models.CharField(
        verbose_name=_('Detected Intent'),
        max_length=100,
        db_column='intent',
        null=True
    )
    
    confidence_score = models.FloatField(
        verbose_name=_('Confidence Score'),
        db_column='confidence_score',
        null=True
    )
    
    metadata = models.JSONField(
        verbose_name=_('Metadata'),
        default=dict,
        null=True,
        db_column='metadata'
    )
    
    is_flagged = models.BooleanField(
        verbose_name=_('Is Flagged'),
        default=False,
        db_column='is_flagged'
    )
    
    flag_reason = models.CharField(
        verbose_name=_('Flag Reason'),
        max_length=255,
        db_column='flag_reason',
        null=True
    )
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name_plural = 'Chat Messages'
        managed = True
        indexes = [
            models.Index(fields=['appointment']),
            models.Index(fields=['session']),
            models.Index(fields=['sender']),
            models.Index(fields=['message_type']),
            models.Index(fields=['intent']),
            models.Index(fields=['is_flagged']),
            models.Index(fields=['createdAt']),
        ]
        ordering = ['createdAt']
    
    def __str__(self):
        if self.appointment:
            return f"Message from {self.sender} - {self.createdAt}"
        else:
            return f"{self.message_type} - {self.intent or 'general'}"
    
    def get_display_text(self):
        """Get message content - supports both old 'message' and new 'content' fields."""
        return self.content or self.message
