from django.contrib import admin
from progress.models import (
    Symptom,
    DailyHealthLog,
    SymptomLog,
    FollowUpRecommendation
)


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'related_dosha', 'is_active']
    list_filter = ['category', 'related_dosha', 'is_active']
    search_fields = ['name']


@admin.register(DailyHealthLog)
class DailyHealthLogAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_name',
        'date',
        'energy_level',
        'digestion_quality',
        'stress_level',
        'sleep_hours'
    ]
    list_filter = ['date', 'bowel_pattern']
    search_fields = ['user__firstName', 'user__lastName']
    readonly_fields = ['createdAt', 'updatedAt']
    
    def get_user_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"
    get_user_name.short_description = 'User'


@admin.register(SymptomLog)
class SymptomLogAdmin(admin.ModelAdmin):
    list_display = ['get_symptom', 'severity', 'get_date']
    list_filter = ['severity', 'symptom__category']
    search_fields = ['daily_log__user__firstName', 'symptom__name']
    
    def get_symptom(self, obj):
        return obj.symptom.name
    get_symptom.short_description = 'Symptom'
    
    def get_date(self, obj):
        return obj.daily_log.date
    get_date.short_description = 'Date'


@admin.register(FollowUpRecommendation)
class FollowUpRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_name',
        'priority',
        'reason',
        'suggested_date',
        'is_booked'
    ]
    list_filter = ['priority', 'reason', 'is_booked', 'suggested_date']
    search_fields = ['user__firstName', 'user__lastName']
    readonly_fields = ['createdAt', 'updatedAt']
    
    def get_user_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"
    get_user_name.short_description = 'User'
