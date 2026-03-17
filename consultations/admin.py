from django.contrib import admin
from consultations.models import ConsultationSession


@admin.register(ConsultationSession)
class ConsultationSessionAdmin(admin.ModelAdmin):
    list_display = ['get_appointment_info', 'status', 'video_provider', 'started_at', 'duration_minutes']
    list_filter = ['status', 'video_provider', 'created_at']
    search_fields = ['appointment__patient__firstName', 'appointment__doctor__user__firstName']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'ended_at']
    
    def get_appointment_info(self, obj):
        return f"Appt #{obj.appointment.id}"
    get_appointment_info.short_description = 'Appointment'
