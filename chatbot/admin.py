from django.contrib import admin
from chatbot.models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['get_user_name', 'context_type', 'is_active', 'message_count', 'createdAt']
    list_filter = ['context_type', 'is_active', 'createdAt']
    search_fields = ['user__firstName', 'user__lastName', 'title']
    readonly_fields = ['message_count', 'createdAt', 'updatedAt']
    
    def get_user_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"
    get_user_name.short_description = 'User'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['get_session_or_appt', 'message_type', 'intent', 'is_flagged', 'createdAt']
    list_filter = ['message_type', 'intent', 'is_flagged', 'createdAt']
    search_fields = ['appointment__id', 'session__title', 'content', 'message']
    readonly_fields = ['intent', 'confidence_score', 'createdAt', 'updatedAt']
    
    def get_session_or_appt(self, obj):
        if obj.session:
            return f"Session: {obj.session.title or obj.session.context_type}"
        elif obj.appointment:
            return f"Appt #{obj.appointment.id}"
        return "No context"
    get_session_or_appt.short_description = 'Context'
