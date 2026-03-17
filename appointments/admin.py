from django.contrib import admin
from appointments.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'get_patient_name',
        'get_doctor_name',
        'date',
        'start_time',
        'status',
        'rating'
    ]
    list_filter = ['status', 'date', 'doctor__specialization']
    search_fields = [
        'patient__firstName',
        'patient__lastName',
        'doctor__user__firstName',
        'doctor__user__lastName'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Info', {
            'fields': ('patient', 'doctor', 'date', 'start_time', 'end_time')
        }),
        ('Status', {
            'fields': ('status', 'cancellation_reason')
        }),
        ('Communication', {
            'fields': ('meeting_link', 'notes')
        }),
        ('Feedback', {
            'fields': ('rating', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.firstName} {obj.doctor.user.lastName}"
    get_doctor_name.short_description = 'Doctor'
