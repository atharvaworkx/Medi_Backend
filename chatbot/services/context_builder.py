from typing import Dict, List, Any
from users.models import Users
from prescriptions.models import Prescription


class ContextBuilder:
    """Build rich context from user data for personalized chatbot responses."""
    
    MAX_TOKENS = 4000
    
    @staticmethod
    def get_user_profile(user: Users) -> Dict[str, Any]:
        """Extract user profile information."""
        try:
            from profiles.models import UserProfile
            profile = UserProfile.objects.get(user=user)
            return {
                'age': getattr(profile, 'age', None),
                'gender': getattr(profile, 'gender', None),
                'constitution': getattr(profile, 'constitution', None),
                'language_preference': getattr(profile, 'language_preference', 'en'),
                'health_goals': getattr(profile, 'health_goals', []),
                'allergies': getattr(profile, 'allergies', ''),
                'chronic_conditions': getattr(profile, 'chronic_conditions', '')
            }
        except:
            return {}
    
    @staticmethod
    def get_latest_report(user: Users) -> Dict[str, Any]:
        """Extract latest AI health report."""
        try:
            from ai_reports.models import HealthAssessmentReport
            report = HealthAssessmentReport.objects.filter(userId=user).first()
            if not report:
                return {}
            
            return {
                'report_id': report.id,
                'dominant_dosha': 'general',
                'risk_level': 'low',
                'is_critical': False,
                'health_summary': 'Health assessment available',
                'recommendations': '',
                'risk_areas': [],
                'created_date': str(report.created_at.date())
            }
        except:
            return {}
    
    @staticmethod
    def get_active_prescriptions(user: Users) -> List[Dict]:
        """Extract active prescriptions."""
        try:
            prescriptions = Prescription.objects.filter(
                patient=user,
                status='active'
            ).order_by('-created_at')[:5]
            
            return [
                {
                    'medicine': script.medicines if hasattr(script, 'medicines') else '',
                    'dosage': getattr(script, 'dosage', ''),
                    'frequency': getattr(script, 'frequency', ''),
                    'duration': getattr(script, 'duration', ''),
                    'purpose': getattr(script, 'notes', '')
                }
                for script in prescriptions
            ]
        except:
            return []
    
    @staticmethod
    def get_recent_health_logs(user: Users, days: int = 7) -> Dict[str, Any]:
        """Extract recent health tracking data."""
        try:
            from progress.models import DailyHealthLog
            from django.utils import timezone
            from datetime import timedelta
            
            start_date = timezone.now().date() - timedelta(days=days)
            logs = DailyHealthLog.objects.filter(
                user=user,
                date__gte=start_date
            ).order_by('-date')[:7]
            
            if not logs:
                return {}
            
            avg_energy = sum(l.energy_level for l in logs) / len(logs)
            avg_digestion = sum(l.digestion_quality for l in logs) / len(logs)
            avg_stress = sum(l.stress_level for l in logs) / len(logs)
            avg_sleep = sum(l.sleep_hours for l in logs) / len(logs)
            
            return {
                'logs_count': len(logs),
                'avg_energy_level': round(avg_energy, 1),
                'avg_digestion_quality': round(avg_digestion, 1),
                'avg_stress_level': round(avg_stress, 1),
                'avg_sleep_hours': round(avg_sleep, 1),
                'recent_symptoms': [log.symptom_notes for log in logs if log.symptom_notes],
                'diet_patterns': [log.diet_notes for log in logs if log.diet_notes]
            }
        except:
            return {}
    
    @staticmethod
    def get_upcoming_appointments(user: Users) -> List[Dict]:
        """Extract upcoming appointments."""
        try:
            from appointments.models import Appointment
            from django.utils import timezone
            
            appointments = Appointment.objects.filter(
                patient=user,
                date__gte=timezone.now().date(),
                status__in=['booked', 'confirmed']
            ).select_related('doctor').order_by('date')[:3]
            
            return [
                {
                    'date': str(appt.date),
                    'time': str(appt.start_time),
                    'doctor': f"Dr. {appt.doctor.user.firstName} {appt.doctor.user.lastName}",
                    'specialization': appt.doctor.specialization.name if appt.doctor.specialization else 'General'
                }
                for appt in appointments
            ]
        except:
            return []
    
    @staticmethod
    def build_context_prompt(user: Users, context_type: str, custom_context: str = None) -> str:
        """Build comprehensive prompt context."""
        profile = ContextBuilder.get_user_profile(user)
        report = ContextBuilder.get_latest_report(user)
        prescriptions = ContextBuilder.get_active_prescriptions(user)
        health_logs = ContextBuilder.get_recent_health_logs(user)
        appointments = ContextBuilder.get_upcoming_appointments(user)
        
        context = f"""### USER PROFILE
- Name: {user.firstName} {user.lastName}
- Language: {profile.get('language_preference', 'English')}

### LATEST HEALTH REPORT
- Status: Available

### ACTIVE PRESCRIPTIONS
{ContextBuilder._format_prescriptions(prescriptions)}

### RECENT HEALTH METRICS (Last 7 Days)
{ContextBuilder._format_health_logs(health_logs)}

### UPCOMING APPOINTMENTS
{ContextBuilder._format_appointments(appointments)}

### CONTEXT TYPE: {context_type.upper()}

---
Provide a personalized, empathetic response based on the user's health context.
"""
        return context[:ContextBuilder.MAX_TOKENS]
    
    @staticmethod
    def _format_prescriptions(prescriptions: List[Dict]) -> str:
        """Format prescriptions for prompt."""
        if not prescriptions:
            return "- No active prescriptions"
        return '\n'.join([f"- {p.get('medicine', 'Unknown')}" for p in prescriptions])
    
    @staticmethod
    def _format_health_logs(logs: Dict) -> str:
        """Format health logs for prompt."""
        if not logs:
            return "- No recent logs"
        return f"- Energy: {logs.get('avg_energy_level', 'N/A')}, Stress: {logs.get('avg_stress_level', 'N/A')}"
    
    @staticmethod
    def _format_appointments(appointments: List[Dict]) -> str:
        """Format appointments for prompt."""
        if not appointments:
            return "- No upcoming appointments"
        return '\n'.join([f"- {a['date']} at {a['time']} with {a['doctor']}" for a in appointments])
