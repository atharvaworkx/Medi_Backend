from django.contrib import admin
from orders.models import Order, OrderItem, Subscription


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['get_order_id', 'get_patient_name', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['patient__firstName', 'patient__lastName', 'id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def get_order_id(self, obj):
        return f"#{obj.id}"
    get_order_id.short_description = 'Order ID'
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"
    get_patient_name.short_description = 'Patient'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'medicine', 'interval', 'next_delivery_date', 'is_active']
    list_filter = ['interval', 'is_active', 'created_at']
    search_fields = ['patient__firstName', 'medicine__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"
    get_patient_name.short_description = 'Patient'
