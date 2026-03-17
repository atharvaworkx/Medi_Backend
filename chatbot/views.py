from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import SimpleRateThrottle
from django.utils import timezone
from datetime import timedelta

from chatbot.models import ChatMessage, ChatSession
from chatbot.serializers import (
    ChatMessageSerializer, ChatMessageCreateSerializer, ChatHistorySerializer,
    ChatSessionSerializer, SendGlobalChatMessageSerializer, ChatResponseSerializer
)
from chatbot.services.assistant import ChatbotAssistant, ContextBuilder
from chatbot.services.global_assistant import GlobalAssistant
from appointments.models import Appointment


class ChatRateThrottle(SimpleRateThrottle):
    """Rate throttle for chatbot API - 30 requests per minute."""
    scope = 'chatbot'
    
    def get_cache_key(self):
        if self.request.user and self.request.user.is_authenticated:
            return f'chatbot_{self.request.user.id}'
        return None


class ChatMessageViewSet(viewsets.ModelViewSet):
    """Manage chatbot messages during consultation."""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatRateThrottle]
    
    def get_queryset(self):
        """Filter messages by user's appointments."""
        user = self.request.user
        
        if hasattr(user, 'doctor_profile'):
            return ChatMessage.objects.filter(
                appointment__doctor=user.doctor_profile
            ).select_related('appointment')
        
        return ChatMessage.objects.filter(
            appointment__patient=user
        ).select_related('appointment')
    
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        """
        Send chat message and get AI response.
        POST /api/consultation-chat/send/
        """
        serializer = ChatMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        appointment = Appointment.objects.get(id=serializer.validated_data['appointment_id'])
        user_message = serializer.validated_data['message']
        
        # Verify access
        if appointment.patient != request.user and appointment.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Determine sender role
        if request.user == appointment.patient:
            sender_role = 'patient'
        else:
            sender_role = 'doctor'
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            appointment=appointment,
            sender=sender_role,
            message=user_message
        )
        
        # Generate AI response
        context = ContextBuilder.build_context(appointment)
        ai_response = ChatbotAssistant.generate_response(user_message, context)
        
        # Save AI message
        ai_msg = ChatMessage.objects.create(
            appointment=appointment,
            sender='ai',
            message=ai_response,
            metadata={'context': str(context)}
        )
        
        # Return both messages
        return Response({
            'status': 'success',
            'user_message': ChatMessageSerializer(user_msg).data,
            'ai_response': ChatMessageSerializer(ai_msg).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get chat history for an appointment.
        GET /api/consultation-chat/history/?appointment_id=1
        """
        appointment_id = request.query_params.get('appointment_id')
        
        if not appointment_id:
            return Response(
                {'error': 'appointment_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify access
        if appointment.patient != request.user and appointment.doctor.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = ChatMessage.objects.filter(appointment=appointment).order_by('createdAt')
        serializer = ChatHistorySerializer(messages, many=True)
        
        return Response({
            'appointment_id': appointment_id,
            'messages': serializer.data
        }, status=status.HTTP_200_OK)


class ChatViewSet(viewsets.ViewSet):
    """Global AI chatbot across platform - independent of appointments."""
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatRateThrottle]
    
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        """
        Send message to global AI chatbot.
        POST /api/chat/send/
        """
        serializer = SendGlobalChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.validated_data['message']
        context_type = serializer.validated_data['context_type']
        session_id = serializer.validated_data.get('session_id')
        
        # Process message with GlobalAssistant
        response_data = GlobalAssistant.process_message(
            user=request.user,
            message=message,
            context_type=context_type,
            session_id=session_id
        )
        
        response_serializer = ChatResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='sessions')
    def list_sessions(self, request):
        """
        Get user's chat sessions.
        GET /api/chat/sessions/?page=1&page_size=10
        """
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        sessions = ChatSession.objects.filter(user=request.user).order_by('-updatedAt')
        total = sessions.count()
        offset = (page - 1) * page_size
        
        sessions_page = sessions[offset:offset + page_size]
        serializer = ChatSessionSerializer(sessions_page, many=True)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='session/(?P<session_id>[^/.]+)')
    def get_session(self, request, session_id=None):
        """
        Get specific chat session with messages.
        GET /api/chat/session/{id}/
        """
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        messages = ChatMessage.objects.filter(session=session).order_by('createdAt')
        session_serializer = ChatSessionSerializer(session)
        message_serializer = ChatMessageSerializer(messages, many=True)
        
        return Response({
            'session': session_serializer.data,
            'messages': message_serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='session/(?P<session_id>[^/.]+)/close')
    def close_session(self, request, session_id=None):
        """
        Close a chat session.
        POST /api/chat/session/{id}/close/
        """
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session.is_active = False
        session.save()
        
        serializer = ChatSessionSerializer(session)
        return Response({
            'message': 'Session closed',
            'session': serializer.data
        }, status=status.HTTP_200_OK)
