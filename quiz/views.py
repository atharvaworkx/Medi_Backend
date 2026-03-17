from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from quiz.models import (
    QuizQuestion, QuizOption, QuizResponse, QuizResult
)
from quiz.serializers import (
    QuizQuestionSerializer, QuizResponseSerializer, QuizResultSerializer
)


class QuizQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuizQuestionSerializer
    permission_classes = [AllowAny]
    queryset = QuizQuestion.objects.filter(isActive=True)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get questions by category"""
        category = request.query_params.get('category')
        if category:
            questions = self.get_queryset().filter(category=category)
            serializer = self.get_serializer(questions, many=True, context={'request': request})
            return Response({
                'status': 'success',
                'category': category,
                'count': questions.count(),
                'questions': serializer.data
            })
        return Response({
            'status': 'error',
            'message': 'Category parameter required'
        }, status=status.HTTP_400_BAD_REQUEST)


class QuizResponseViewSet(viewsets.ModelViewSet):
    serializer_class = QuizResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizResponse.objects.filter(userId=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create or update response"""
        data = request.data
        question_id = data.get('questionId')

        try:
            quiz_response, created = QuizResponse.objects.update_or_create(
                userId=request.user,
                questionId_id=question_id,
                defaults={'responseValue': data.get('responseValue'), 'selectedOptionId_id': data.get('selectedOptionId')}
            )
            serializer = self.get_serializer(quiz_response, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='bulk-submit')
    def bulk_submit(self, request):
        """
        Submit all quiz responses in one call.
        Body: { "responses": [{ "questionId": "...", "selectedOptionId": "...", "responseValue": "..." }, ...] }
        Returns computed dosha scores.
        """
        responses_data = request.data.get('responses', [])
        if not responses_data:
            return Response({'status': 'error', 'message': 'No responses provided'}, status=status.HTTP_400_BAD_REQUEST)

        dosha_scores = {'vata': 0.0, 'pitta': 0.0, 'kapha': 0.0}
        saved_responses = []

        for entry in responses_data:
            question_id = entry.get('questionId')
            option_id = entry.get('selectedOptionId')
            value = entry.get('responseValue', '')

            try:
                quiz_response, _ = QuizResponse.objects.update_or_create(
                    userId=request.user,
                    questionId_id=question_id,
                    defaults={'responseValue': value, 'selectedOptionId_id': option_id}
                )
                saved_responses.append(quiz_response)

                # Accumulate dosha scores from the option's scoreData
                from quiz.models import QuizOption
                try:
                    opt = QuizOption.objects.get(id=option_id)
                    score_data = opt.scoreData or {}
                    for dosha in dosha_scores:
                        dosha_scores[dosha] += float(score_data.get(dosha, 0))
                except QuizOption.DoesNotExist:
                    pass
            except Exception:
                pass

        # Normalize to percentages
        total = sum(dosha_scores.values()) or 1
        prakriti_scores = {k: round(v / total * 100, 2) for k, v in dosha_scores.items()}
        dominant = max(prakriti_scores, key=prakriti_scores.get)

        # Save or update QuizResult
        result, _ = QuizResult.objects.update_or_create(
            userId=request.user,
            defaults={
                'prakritScores': prakriti_scores,
                'vikritScores': prakriti_scores,  # simplified: same as prakriti for now
                'dominantPrakriti': dominant,
                'dominantVikriti': dominant,
            }
        )

        return Response({
            'status': 'success',
            'prakritScores': prakriti_scores,
            'dominantPrakriti': dominant,
            'totalAnswered': len(saved_responses),
        }, status=status.HTTP_200_OK)

