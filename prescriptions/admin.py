from django.contrib import admin
from prescriptions.models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_doctor_name', 'appointment', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['patient__firstName', 'doctor__user__firstName', 'appointment__id']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.firstName} {obj.doctor.user.lastName}"
    get_doctor_name.short_description = 'Doctor'
