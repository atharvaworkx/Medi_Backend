from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from progress.models import (
    DailyHealthLog,
    Symptom,
    SymptomLog,
    FollowUpRecommendation
)
from progress.serializers import (
    DailyHealthLogSerializer,
    CreateDailyHealthLogSerializer,
    FollowUpRecommendationSerializer,
    ProgressAnalyticsSerializer,
    SymptomSerializer
)
from progress.services.progress_analyzer import ProgressAnalyzer
from progress.services.followup_engine import FollowUpEngine


class SymptomViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of trackable symptoms."""
    queryset = Symptom.objects.filter(is_active=True)
    serializer_class = SymptomSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'related_dosha']
    ordering_fields = ['name', 'category']
    ordering = ['name']


class ProgressViewSet(viewsets.ViewSet):
    """Health progress tracking and analytics."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='log')
    def create_log(self, request):
        """POST /api/progress/log/"""
        serializer = CreateDailyHealthLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        date = serializer.validated_data['date']
        
        with transaction.atomic():
            daily_log, created = DailyHealthLog.objects.update_or_create(
                user=request.user,
                date=date,
                defaults={
                    'energy_level': serializer.validated_data['energy_level'],
                    'digestion_quality': serializer.validated_data['digestion_quality'],
                    'stress_level': serializer.validated_data['stress_level'],
                    'sleep_hours': serializer.validated_data['sleep_hours'],
                    'diet_notes': serializer.validated_data.get('diet_notes'),
                    'symptom_notes': serializer.validated_data.get('symptom_notes'),
                    'bowel_pattern': serializer.validated_data.get('bowel_pattern'),
                    'exercise_notes': serializer.validated_data.get('exercise_notes'),
                    'mood_notes': serializer.validated_data.get('mood_notes'),
                }
            )
            
            symptoms = serializer.validated_data.get('symptoms', [])
            for symptom_data in symptoms:
                symptom_id = symptom_data.get('symptom_id')
                severity = symptom_data.get('severity', 1)
                
                try:
                    symptom = Symptom.objects.get(id=symptom_id)
                    SymptomLog.objects.update_or_create(
                        daily_log=daily_log,
                        symptom=symptom,
                        defaults={'severity': severity}
                    )
                except Symptom.DoesNotExist:
                    pass
            
            FollowUpEngine.generate_recommendation(request.user)
        
        response_serializer = DailyHealthLogSerializer(daily_log)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='summary')
    def analytics_summary(self, request):
        """GET /api/progress/summary/?period=30"""
        period = int(request.query_params.get('period', 30))
        
        analytics = ProgressAnalyzer.generate_analytics(request.user, days=period)
        
        serializer = ProgressAnalyticsSerializer(analytics)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='logs')
    def get_logs(self, request):
        """GET /api/progress/logs/?days=30"""
        days = int(request.query_params.get('days', 30))
        
        from datetime import timedelta
        from django.utils import timezone
        start_date = timezone.now().date() - timedelta(days=days)
        
        logs = DailyHealthLog.objects.filter(
            user=request.user,
            date__gte=start_date
        ).prefetch_related('symptom_logs__symptom').order_by('-date')
        
        page = int(request.query_params.get('page', 1))
        page_size = 10
        total = logs.count()
        offset = (page - 1) * page_size
        logs = logs[offset:offset + page_size]
        
        serializer = DailyHealthLogSerializer(logs, many=True)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='recommendations')
    def get_recommendations(self, request):
        """GET /api/progress/recommendations/"""
        recommendations = FollowUpRecommendation.objects.filter(
            user=request.user,
            is_booked=False
        ).select_related('recommended_doctor__user', 'recommended_doctor__specialization').order_by('-priority')
        
        serializer = FollowUpRecommendationSerializer(recommendations, many=True)
        return Response({
            'count': recommendations.count(),
            'recommendations': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='book-followup')
    def book_followup(self, request):
        """POST /api/progress/book-followup/"""
        from appointments.services.appointment_service import AppointmentService
        
        rec_id = request.data.get('recommendation_id')
        doctor_id = request.data.get('doctor_id')
        date = request.data.get('date')
        start_time = request.data.get('start_time')
        
        try:
            recommendation = FollowUpRecommendation.objects.get(
                id=rec_id,
                user=request.user
            )
        except FollowUpRecommendation.DoesNotExist:
            return Response(
                {'error': 'Recommendation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from datetime import datetime
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
        
        appointment, response = AppointmentService.book_appointment(
            patient=request.user,
            doctor_id=doctor_id,
            date=date_obj,
            start_time=start_time_obj,
            notes=f'Follow-up for: {recommendation.reason}'
        )
        
        if appointment:
            recommendation.is_booked = True
            recommendation.related_appointment = appointment
            recommendation.save()
            
            response['recommendation_id'] = rec_id
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
