from django.urls import path
from rest_framework.routers import DefaultRouter
from chatbot.views import ChatMessageViewSet, ChatViewSet

router = DefaultRouter()
router.register(r'consultation-chat', ChatMessageViewSet, basename='consultation-chat')
router.register(r'chat', ChatViewSet, basename='chat')

urlpatterns = router.urls
