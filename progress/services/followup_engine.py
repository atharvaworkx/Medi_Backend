import logging
from django.db import transaction
from progress.models import (
    DailyHealthLog,
    FollowUpRecommendation,
    SymptomLog
)
from progress.services.progress_analyzer import ProgressAnalyzer
from datetime import datetime, timedelta
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class FollowUpEngine:
    """Service to generate follow-up recommendations based on health data."""
    
    HIGH_STRESS_DAYS_THRESHOLD = 7
    IMPROVEMENT_WAIT_DAYS = 14
    
    @staticmethod
    def check_severe_symptom_trend(user) -> Tuple[bool, str]:
        """Check if user has worsening symptom trends."""
        recent_logs = DailyHealthLog.objects.filter(
            user=user
        ).order_by('-date')[:14]
        
        if len(recent_logs) < 7:
            return False, ''
        
        symptom_logs_recent = SymptomLog.objects.filter(
            daily_log__in=recent_logs
        ).select_related('symptom')
        
        high_severity = symptom_logs_recent.filter(severity__gte=4).count()
        
        if high_severity > 5:
            return True, 'Severe symptom trend detected - multiple high-severity symptoms'
        
        return False, ''
    
    @staticmethod
    def check_stress_trend(user) -> Tuple[bool, str]:
        """Check for prolonged high stress."""
        recent_logs = DailyHealthLog.objects.filter(
            user=user
        ).order_by('-date')[:FollowUpEngine.HIGH_STRESS_DAYS_THRESHOLD]
        
        if len(recent_logs) < FollowUpEngine.HIGH_STRESS_DAYS_THRESHOLD:
            return False, ''
        
        high_stress_count = sum(1 for log in recent_logs if log.stress_level >= 8)
        
        if high_stress_count >= 5:
            return True, f'High stress persisting for {high_stress_count}/{len(recent_logs)} days'
        
        return False, ''
    
    @staticmethod
    def check_no_improvement_after_prescription(user) -> Tuple[bool, str]:
        """Check if patient has not improved after prescription."""
        from prescriptions.models import Prescription
        
        prescription = Prescription.objects.filter(
            patient=user,
            is_active=True
        ).order_by('-created_at').first()
        
        if not prescription or not prescription.created_at:
            return False, ''
        
        days_since_prescription = (datetime.now() - prescription.created_at.replace(tzinfo=None)).days
        
        if days_since_prescription < FollowUpEngine.IMPROVEMENT_WAIT_DAYS:
            return False, ''
        
        logs, _, _ = ProgressAnalyzer.get_period_logs(
            user,
            days=days_since_prescription
        )
        
        if len(logs) < 7:
            return False, ''
        
        first_half = logs[:len(logs)//2]
        second_half = logs[len(logs)//2:]
        
        first_digestion = sum(l.digestion_quality for l in first_half) / len(first_half)
        second_digestion = sum(l.digestion_quality for l in second_half) / len(second_half)
        
        improvement = (second_digestion - first_digestion) / first_digestion * 100
        
        if improvement < 5:
            return True, f'Minimal improvement {improvement:.1f}% - {days_since_prescription} days post-prescription'
        
        return False, ''
    
    @staticmethod
    def check_doctor_recommended_followup(user) -> Tuple[bool, str]:
        """Check if doctor set a follow-up recommendation."""
        from appointments.models import Appointment
        
        last_appointment = Appointment.objects.filter(
            patient=user,
            status='completed'
        ).order_by('-date').first()
        
        if not last_appointment:
            return False, ''
        
        if last_appointment.notes and any(
            keyword in last_appointment.notes.lower()
            for keyword in ['follow-up', 'followup', 'revisit', 'follow up']
        ):
            return True, 'Doctor recommended follow-up in appointment notes'
        
        return False, ''
    
    @classmethod
    @transaction.atomic
    def generate_recommendation(cls, user) -> FollowUpRecommendation:
        """
        Generate follow-up recommendation if criteria met.
        
        Returns:
            FollowUpRecommendation instance or None
        """
        severe_trend, severe_reason = cls.check_severe_symptom_trend(user)
        stress_trend, stress_reason = cls.check_stress_trend(user)
        no_improvement, no_improvement_reason = cls.check_no_improvement_after_prescription(user)
        doctor_recommended, doctor_reason = cls.check_doctor_recommended_followup(user)
        
        should_recommend = severe_trend or stress_trend or no_improvement or doctor_recommended
        
        if not should_recommend:
            return None
        
        if severe_trend:
            priority = 'high' if stress_trend else 'medium'
            reason = 'severe_symptoms'
            description = severe_reason
        elif stress_trend:
            priority = 'high' if no_improvement else 'medium'
            reason = 'high_stress'
            description = stress_reason
        elif no_improvement:
            priority = 'medium'
            reason = 'no_improvement'
            description = no_improvement_reason
        else:
            priority = 'low'
            reason = 'doctor_recommended'
            description = doctor_reason
        
        from datetime import date
        days_offset = 7 if priority in ['high', 'critical'] else 14
        suggested_date = date.today() + timedelta(days=days_offset)
        
        try:
            from doctors.services.doctor_matching import DoctorMatchingService
            recommended_doctors, _ = DoctorMatchingService.match_doctors(user, limit=1)
            recommended_doctor = recommended_doctors[0] if recommended_doctors else None
        except:
            recommended_doctor = None
        
        recommendation = FollowUpRecommendation.objects.create(
            user=user,
            recommended_doctor=recommended_doctor,
            suggested_date=suggested_date,
            priority=priority,
            reason=reason,
            description=description,
            is_booked=False
        )
        
        return recommendation
    
    @staticmethod
    def get_pending_recommendations(user):
        """Get all unbooked pending recommendations."""
        from datetime import datetime as dt
        return FollowUpRecommendation.objects.filter(
            user=user,
            is_booked=False,
            suggested_date__gte=dt.now().date()
        ).select_related('recommended_doctor').order_by('-priority')
