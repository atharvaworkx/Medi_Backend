from django.urls import path, include
from rest_framework.routers import DefaultRouter
from quiz.views import QuizQuestionViewSet, QuizResponseViewSet

router = DefaultRouter()
router.register(r'questions', QuizQuestionViewSet, basename='question')
router.register(r'responses', QuizResponseViewSet, basename='response')

urlpatterns = [
    path('', include(router.urls)),
]
