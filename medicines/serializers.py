from rest_framework import serializers
from medicines.models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    """Serializer for medicines."""
    
    class Meta:
        model = Medicine
        fields = [
            'id',
            'name',
            'category',
            'description',
            'dosage_info',
            'dosha_affinity',
            'price',
            'stock_quantity',
            'is_active'
        ]
        read_only_fields = ['id']


class MedicineRecommendationSerializer(serializers.Serializer):
    """Serializer for medicine recommendations."""
    
    medicine_id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    dosage_info = serializers.CharField()
    price = serializers.CharField()
    stock_available = serializers.IntegerField()
    dosha_affinity = serializers.CharField()
    relevance_score = serializers.FloatField()
    description = serializers.CharField()
