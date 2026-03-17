from appointments.models import Appointment
from ai_reports.models import HealthAssessmentReport
from typing import Dict, Optional


class ContextBuilder:
    """Build context for chatbot from user medical history."""
    
    @staticmethod
    def build_context(appointment: Appointment) -> Dict:
        """Build comprehensive context from appointment and medical history."""
        patient = appointment.patient
        
        # Get latest health assessment report
        ai_report = HealthAssessmentReport.objects.filter(userId=patient).first()
        
        context = {
            'patient_name': f"{patient.firstName} {patient.lastName}",
            'doctor_name': f"Dr. {appointment.doctor.user.firstName} {appointment.doctor.user.lastName}",
            'appointment_id': appointment.id,
            'dosha_info': {},
            'risk_flags': {},
            'medical_history': {}
        }
        
        if ai_report:
            # Extract dosha scores from prakritResult
            prakriti = ai_report.prakritResult or {}
            vata = prakriti.get('vata', 0)
            pitta = prakriti.get('pitta', 0)
            kapha = prakriti.get('kapha', 0)
            
            # Determine dominant dosha
            dominant_dosha = 'general'
            max_score = max(vata, pitta, kapha)
            if max_score > 0:
                if vata == max_score:
                    dominant_dosha = 'vata'
                elif pitta == max_score:
                    dominant_dosha = 'pitta'
                elif kapha == max_score:
                    dominant_dosha = 'kapha'
            
            context['dosha_info'] = {
                'dominant_dosha': dominant_dosha,
                'vata_score': vata,
                'pitta_score': pitta,
                'kapha_score': kapha,
            }
            
            # Extract risk information
            digestive_risk = ai_report.digestiveRisk or {}
            risk_level = digestive_risk.get('risk_level', 'low')
            is_critical = risk_level == 'high'
            
            context['risk_flags'] = {
                'is_critical': is_critical,
                'risk_level': risk_level,
                'risk_areas': [r.get('area') for r in digestive_risk.get('details', [])],
            }
        
        return context


class ChatbotAssistant:
    """AI chatbot assistant for consultation."""
    
    AYURVEDIC_SUGGESTIONS = {
        'vata': {
            'practices': ['Abhyanga (oil massage)', 'Warm foods', 'Regular routine', 'Meditation'],
            'foods': ['Warm soups', 'Ghee', 'Sesame oil', 'Grains'],
            'activities': ['Yoga', 'Walking', 'Deep breathing']
        },
        'pitta': {
            'practices': ['Cooling water therapies', 'Meditation', 'Rest', 'Moonlight walks'],
            'foods': ['Coconut', 'Cucumber', 'Leafy greens', 'Cooling spices'],
            'activities': ['Swimming', 'Gentle yoga', 'Breathing exercises']
        },
        'kapha': {
            'practices': ['Dry massage', 'Heating therapies', 'Active lifestyle'],
            'foods': ['Warming spices', 'Bitter greens', 'Legumes', 'Light foods'],
            'activities': ['Vigorous exercise', 'Hiking', 'Dance']
        }
    }
    
    @staticmethod
    def generate_response(user_message: str, context: Dict) -> str:
        """Generate chatbot response based on message and context."""
        message_lower = user_message.lower()
        
        # Keyword-based responses (stub for future LLM integration)
        if any(word in message_lower for word in ['yogurt', 'diet', 'food', 'eat']):
            return ChatbotAssistant._dietary_suggestions(context)
        
        if any(word in message_lower for word in ['exercise', 'yoga', 'activity', 'routine']):
            return ChatbotAssistant._lifestyle_suggestions(context)
        
        if any(word in message_lower for word in ['medicine', 'treatment', 'prescription']):
            return "Please wait for the doctor's prescription. I'm here to assist with general Ayurvedic guidance."
        
        # Default response
        dominant_dosha = context.get('dosha_info', {}).get('dominant_dosha', 'general')
        if dominant_dosha in ChatbotAssistant.AYURVEDIC_SUGGESTIONS:
            suggestions = ChatbotAssistant.AYURVEDIC_SUGGESTIONS[dominant_dosha]
            return f"Based on your {dominant_dosha} constitution, here are some recommendations:\n\nPractices: {', '.join(suggestions['practices'])}"
        
        return "I'm here to assist with Ayurvedic wellness guidance. How can I help?"
    
    @staticmethod
    def _dietary_suggestions(context: Dict) -> str:
        """Generate dietary recommendations."""
        dominant_dosha = context.get('dosha_info', {}).get('dominant_dosha', 'general')
        if dominant_dosha in ChatbotAssistant.AYURVEDIC_SUGGESTIONS:
            foods = ChatbotAssistant.AYURVEDIC_SUGGESTIONS[dominant_dosha]['foods']
            return f"For your {dominant_dosha} balance, recommended foods include: {', '.join(foods)}"
        return "Consult with Dr. {doctor_name} for personalized dietary advice.".format(**context)
    
    @staticmethod
    def _lifestyle_suggestions(context: Dict) -> str:
        """Generate lifestyle recommendations."""
        dominant_dosha = context.get('dosha_info', {}).get('dominant_dosha', 'general')
        if dominant_dosha in ChatbotAssistant.AYURVEDIC_SUGGESTIONS:
            activities = ChatbotAssistant.AYURVEDIC_SUGGESTIONS[dominant_dosha]['activities']
            return f"For your {dominant_dosha} balance, beneficial activities include: {', '.join(activities)}"
        return "Consult with Dr. {doctor_name} for a personalized activity plan.".format(**context)
