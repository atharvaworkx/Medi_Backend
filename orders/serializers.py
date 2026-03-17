from rest_framework import serializers
from orders.models import Order, OrderItem, Subscription
from medicines.models import Medicine


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'medicine', 'medicine_name', 'quantity', 'price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'patient',
            'patient_name',
            'total_amount',
            'status',
            'payment_status',
            'items',
            'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'patient']
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"


class CheckoutItemSerializer(serializers.Serializer):
    """Serializer for checkout items."""
    
    medicine_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout."""
    
    items = CheckoutItemSerializer(many=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id',
            'patient',
            'patient_name',
            'medicine',
            'medicine_name',
            'quantity',
            'interval',
            'next_delivery_date',
            'is_active'
        ]
        read_only_fields = ['id', 'patient']
    
    def get_patient_name(self, obj):
        return f"{obj.patient.firstName} {obj.patient.lastName}"


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating subscriptions."""
    
    medicine_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    interval = serializers.ChoiceField(
        choices=['monthly', 'quarterly', 'biannual', 'annual']
    )
    
    def validate_medicine_id(self, value):
        try:
            Medicine.objects.get(id=value, is_active=True)
            return value
        except Medicine.DoesNotExist:
            raise serializers.ValidationError('Medicine not found or inactive')
