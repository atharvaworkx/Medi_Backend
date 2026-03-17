from django.contrib import admin
from medicines.models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'dosha_affinity', 'price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'dosha_affinity', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
