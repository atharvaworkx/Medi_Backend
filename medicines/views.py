from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from medicines.models import Medicine
from medicines.serializers import MedicineSerializer, MedicineRecommendationSerializer
from medicines.services.medicine_recommender import MedicineRecommender
from prescriptions.models import Prescription


class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    """Browse medicine catalog."""
    
    queryset = Medicine.objects.filter(is_active=True).order_by('name')
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recommend(self, request):
        """
        Get medicine recommendations for a prescription.
        GET /api/medicines/recommend/?prescription_id=1
        """
        prescription_id = request.query_params.get('prescription_id')
        
        if not prescription_id:
            return Response(
                {'error': 'prescription_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            prescription = Prescription.objects.get(id=prescription_id)
        except Prescription.DoesNotExist:
            return Response(
                {'error': 'Prescription not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify access
        if prescription.patient != request.user and prescription.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        recommendations = MedicineRecommender.recommend_medicines(prescription)
        
        serializer = MedicineRecommendationSerializer(recommendations, many=True)
        return Response({
            'prescription_id': prescription_id,
            'recommended_medicines': serializer.data,
            'based_on': 'Dosha + Prescription'
        }, status=status.HTTP_200_OK)
