import logging
from django.db.models import Q, F
from doctors.models import Doctor, Specialization, DoctorAvailability
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)

class DoctorMatchingService:
    """Service to match patients with appropriate doctors based on AI reports."""
    
    DOSHA_SPECIALIZATION_MAP = {
        'vata': ['nervous', 'anxiety', 'mental', 'sleep'],
        'pitta': ['digestive', 'inflammation', 'skin', 'liver'],
        'kapha': ['respiratory', 'weight', 'immunity', 'joint'],
    }
    
    RISK_CATEGORY_MAP = {
        'high': 'critical',
        'medium': 'specialized',
        'low': 'preventive',
    }
    
    @staticmethod
    def get_latest_report(user):
        """Fetch latest AI report for user."""
        from ai_reports.models import AIReport
        try:
            return AIReport.objects.filter(user=user).order_by('-created_at').first()
        except Exception:
            return None
    
    @staticmethod
    def extract_risk_flags(report) -> Dict:
        """Extract risk flags from AI report."""
        if not report:
            return {}
        
        flags = {
            'dominant_dosha': getattr(report, 'dominant_dosha', None),
            'is_critical': getattr(report, 'is_critical', False),
            'risk_level': getattr(report, 'risk_level', 'low'),
            'risk_areas': getattr(report, 'risk_areas', []),
        }
        return flags
    
    @classmethod
    def match_doctors(cls, user, limit: int = None) -> Tuple[List[Doctor], bool]:
        """
        Match patient with appropriate doctors.
        
        Returns:
            Tuple of (list of doctors, is_critical_flag)
        """
        report = cls.get_latest_report(user)
        risk_flags = cls.extract_risk_flags(report)
        
        is_critical = risk_flags.get('is_critical', False)
        dominant_dosha = risk_flags.get('dominant_dosha', 'general')
        risk_level = risk_flags.get('risk_level', 'low')
        
        # Start with base query
        doctors_query = Doctor.objects.filter(
            is_available=True,
            is_verified=True
        ).select_related('specialization', 'user').prefetch_related('availability_slots')
        
        # Filter by category based on risk level
        category = cls.RISK_CATEGORY_MAP.get(risk_level, 'preventive')
        doctors_query = doctors_query.filter(
            specialization__category=category
        )
        
        # If critical, limit to critical care specialists
        if is_critical:
            doctors_query = doctors_query.filter(
                specialization__category='critical'
            )
            limit = limit or 3
        
        # Filter by dosha specialization
        if dominant_dosha and dominant_dosha != 'general':
            doctors_query = doctors_query.filter(
                Q(specialization__related_dosha=dominant_dosha) |
                Q(specialization__related_dosha='general')
            )
        
        # Rank by experience and rating
        doctors_query = doctors_query.annotate(
            match_score=F('years_of_experience') * 0.3 + F('rating') * 0.7
        ).order_by('-match_score', '-rating')
        
        if limit:
            doctors_query = doctors_query[:limit]
        
        return list(doctors_query), is_critical
    
    @staticmethod
    def validate_doctor_availability(doctor: Doctor, date, start_time) -> bool:
        """Check if doctor has availability on given date and time."""
        day_of_week = date.weekday()
        
        slots = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )
        
        for slot in slots:
            if slot.start_time <= start_time < slot.end_time:
                return True
        
        return False
