from typing import Dict, Tuple
import re
from django.db import transaction
from chatbot.services.context_builder import ContextBuilder
from users.models import Users
import logging

logger = logging.getLogger(__name__)


class GlobalAssistant:
    """Global AI chatbot assistant with multi-intent routing."""
    
    INTENT_PATTERNS = {
        'report_explanation': [
            r'explain.*report', r'understand.*report', r'what.*report',
            r'my.*health.*report', r'report.*mean'
        ],
        'medicine_clarification': [
            r'medicine', r'prescription', r'drug', r'take.*pill',
            r'side.*effect', r'dosage'
        ],
        'lifestyle_suggestion': [
            r'lifestyle', r'routine', r'habit', r'exercise', r'workout'
        ],
        'diet_suggestion': [
            r'diet', r'food', r'eat', r'nutrition', r'recipe'
        ],
        'symptom_guidance': [
            r'symptom', r'feeling', r'pain', r'ache', r'problem'
        ],
        'doctor_consultation': [
            r'consult.*doctor', r'see.*doctor', r'appointment', r'urgent'
        ],
        'stress_management': [
            r'stress', r'anxiety', r'worry', r'tension', r'calm'
        ],
        'sleep_improvement': [
            r'sleep', r'insomnia', r'tired', r'fatigue', r'rest'
        ],
    }
    
    @staticmethod
    def detect_intent(message: str) -> Tuple[str, float]:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        for intent, patterns in GlobalAssistant.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent, 0.8
        
        return 'general', 0.5
    
    @staticmethod
    def check_critical_keywords(message: str) -> Tuple[bool, str]:
        """Check for critical/emergency keywords."""
        critical_keywords = [
            'emergency', 'urgent', 'critical', 'severe', 'chest pain',
            'difficulty breathing', 'loss of consciousness', 'bleeding'
        ]
        
        message_lower = message.lower()
        for keyword in critical_keywords:
            if keyword in message_lower:
                return True, keyword
        
        return False, ''
    
    @staticmethod
    def _generate_response(
        user: Users,
        message: str,
        intent: str,
        is_critical: bool,
        context: str
    ) -> Dict:
        """Generate personalized response based on intent."""
        
        if is_critical:
            return {
                'reply': (
                    "⚠️ URGENT: Please seek immediate medical attention or call emergency services. "
                    "I'm not a substitute for emergency care."
                ),
                'suggestions': ['Call emergency', 'Visit hospital', 'Contact doctor'],
                'recommended_actions': ['seek_emergency_care'],
                'confidence': 1.0
            }
        
        intent_responses = {
            'report_explanation': {
                'reply': (
                    "Based on your health report, I can help explain specific aspects. "
                    "What particular aspects would you like to understand better?"
                ),
                'suggestions': ['Dosha explanation', 'Health risks', 'Improvements'],
                'recommended_actions': ['view_full_report']
            },
            'medicine_clarification': {
                'reply': (
                    "I'm here to help clarify how to take your medicines safely. "
                    "Always follow your doctor's instructions. What specific medicine?"
                ),
                'suggestions': ['Dosage info', 'Side effects', 'When to take'],
                'recommended_actions': ['contact_doctor']
            },
            'lifestyle_suggestion': {
                'reply': (
                    "Based on your health profile, I recommend maintaining a balanced routine. "
                    "Would you like specific tips for morning routine or exercise?"
                ),
                'suggestions': ['Morning routine', 'Exercise tips', 'Sleep schedule'],
                'recommended_actions': ['update_lifestyle']
            },
            'diet_suggestion': {
                'reply': (
                    "Here are personalized diet suggestions for your constitution. "
                    "Include warm, nourishing foods and avoid very cold items."
                ),
                'suggestions': ['Foods to eat', 'Foods to avoid', 'Meal timing'],
                'recommended_actions': ['update_diet']
            },
            'symptom_guidance': {
                'reply': (
                    "I understand you're experiencing symptoms. "
                    "Professional evaluation is important. Would you like to schedule a consultation?"
                ),
                'suggestions': ['Book appointment', 'Log symptoms', 'Health history'],
                'recommended_actions': ['book_appointment', 'log_symptoms']
            },
            'general': {
                'reply': (
                    "I'm your health companion! I can help with explaining reports, "
                    "clarifying medicines, suggesting lifestyle changes, and scheduling consultations. "
                    "How can I assist?"
                ),
                'suggestions': ['Explain report', 'Lifestyle help', 'Medicine info'],
                'recommended_actions': []
            }
        }
        
        response = intent_responses.get(intent, intent_responses['general'])
        response['confidence'] = 0.85
        
        return response
    
    @classmethod
    @transaction.atomic
    def process_message(
        cls,
        user: Users,
        message: str,
        context_type: str = 'general',
        session_id: int = None
    ) -> Dict:
        """Process user message and generate response."""
        from chatbot.models import ChatSession, ChatMessage
        
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=user)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(
                    user=user,
                    context_type=context_type
                )
        else:
            session = ChatSession.objects.create(
                user=user,
                context_type=context_type,
                title=message[:50]
            )
        
        is_critical, critical_keyword = cls.check_critical_keywords(message)
        intent, confidence = cls.detect_intent(message)
        
        context_prompt = ContextBuilder.build_context_prompt(
            user=user,
            context_type=context_type,
            custom_context=message
        )
        
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message,
            intent=intent,
            confidence_score=confidence,
            metadata={'is_critical': is_critical}
        )
        
        response_data = cls._generate_response(
            user=user,
            message=message,
            intent=intent,
            is_critical=is_critical,
            context=context_prompt
        )
        
        ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=response_data['reply'],
            intent=intent,
            confidence_score=response_data.get('confidence', 0.9),
            metadata={
                'suggestions': response_data.get('suggestions', []),
                'recommended_actions': response_data.get('recommended_actions', [])
            },
            is_flagged=is_critical,
            flag_reason=f'Critical: {critical_keyword}' if is_critical else None
        )
        
        session.message_count += 2
        session.is_active = True
        session.save()
        
        logger.info(f"Chat - User: {user.id}, Intent: {intent}, Critical: {is_critical}")
        
        return {
            'session_id': session.id,
            'reply': response_data['reply'],
            'suggestions': response_data.get('suggestions', []),
            'recommended_actions': response_data.get('recommended_actions', []),
            'is_critical': is_critical,
            'intent': intent
        }
