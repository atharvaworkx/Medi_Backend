from django.contrib import admin
from doctors.models import Doctor, Specialization, DoctorAvailability


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'related_dosha', 'category', 'is_active']
    list_filter = ['category', 'related_dosha', 'is_active']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialization', 'years_of_experience', 'rating', 'is_available', 'is_verified']
    list_filter = ['specialization', 'is_available', 'is_verified']
    search_fields = ['user__firstName', 'user__lastName']
    
    def get_full_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"
    get_full_name.short_description = 'Doctor Name'


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_day_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    search_fields = ['doctor__user__firstName']
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'
