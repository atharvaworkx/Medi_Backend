from rest_framework import serializers
from chatbot.models import ChatMessage, ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'context_type', 'is_active', 'title', 
            'related_report', 'message_count', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'message_count', 'createdAt', 'updatedAt']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages - extended for both consultation and global chats."""
    
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'appointment', 'session', 'sender', 'sender_display', 
            'message_type', 'message_type_display', 'message', 'content', 'intent', 
            'confidence_score', 'is_flagged', 'flag_reason', 'metadata', 
            'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'intent', 'confidence_score', 'is_flagged', 
                           'flag_reason', 'createdAt', 'updatedAt']


class ChatMessageCreateSerializer(serializers.Serializer):
    """Serializer for creating chat messages - consultation-specific."""
    
    appointment_id = serializers.IntegerField()
    message = serializers.CharField(max_length=2000)
    
    def validate_appointment_id(self, value):
        from appointments.models import Appointment
        try:
            Appointment.objects.get(id=value)
            return value
        except Appointment.DoesNotExist:
            raise serializers.ValidationError('Appointment not found')


class SendGlobalChatMessageSerializer(serializers.Serializer):
    """Serializer for sending messages to global AI chatbot."""
    
    message = serializers.CharField(max_length=2000)
    context_type = serializers.ChoiceField(
        choices=[
            ('general', 'General Health Question'),
            ('consultation', 'Consultation Related'),
            ('followup', 'Follow-up Discussion'),
            ('report_discussion', 'Report Discussion'),
            ('prescription', 'Prescription Clarification'),
            ('lifestyle', 'Lifestyle & Diet'),
        ],
        default='general'
    )
    session_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_session_id(self, value):
        if value:
            try:
                ChatSession.objects.get(id=value)
                return value
            except ChatSession.DoesNotExist:
                raise serializers.ValidationError('Session not found')
        return value


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chatbot response."""
    
    session_id = serializers.IntegerField(read_only=True)
    message_id = serializers.IntegerField(read_only=True)
    reply = serializers.CharField(read_only=True)
    intent = serializers.CharField(read_only=True)
    confidence_score = serializers.FloatField(read_only=True)
    is_critical = serializers.BooleanField(read_only=True)
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    recommended_actions = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for chat history."""
    
    sender_display = serializers.CharField(source='get_sender_display', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'sender_display', 'message_type', 'message_type_display',
            'message', 'content', 'intent', 'is_flagged', 'createdAt'
        ]
