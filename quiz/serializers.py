from rest_framework import serializers
from atomicloops.serializers import AtomicSerializer
from quiz.models import QuizQuestion, QuizOption, QuizResponse, QuizResult


class QuizOptionSerializer(AtomicSerializer):
    class Meta:
        model = QuizOption
        fields = ['id', 'createdAt', 'updatedAt', 'questionId', 'optionText', 'optionValue', 'scoreData', 'order']
        get_fields = ['id', 'createdAt', 'updatedAt', 'questionId', 'optionText', 'optionValue', 'scoreData', 'order']
        list_fields = ['id', 'optionText', 'optionValue', 'order']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class QuizQuestionSerializer(AtomicSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ['id', 'createdAt', 'updatedAt', 'questionText', 'questionType', 'category', 'order', 'isActive', 'options']
        get_fields = ['id', 'createdAt', 'updatedAt', 'questionText', 'questionType', 'category', 'order', 'isActive', 'options']
        list_fields = ['id', 'questionText', 'category', 'order']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class QuizResponseSerializer(AtomicSerializer):
    class Meta:
        model = QuizResponse
        fields = ['id', 'createdAt', 'updatedAt', 'userId', 'questionId', 'selectedOptionId', 'responseValue']
        get_fields = ['id', 'createdAt', 'updatedAt', 'userId', 'questionId', 'selectedOptionId', 'responseValue']
        list_fields = ['id', 'createdAt', 'questionId', 'responseValue']
        read_only_fields = ['id', 'userId', 'createdAt', 'updatedAt']


class QuizResultSerializer(AtomicSerializer):
    class Meta:
        model = QuizResult
        fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'prakritScores', 'vikritScores',
            'dominantPrakriti', 'dominantVikriti', 'completedAt'
        ]
        get_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'prakritScores', 'vikritScores',
            'dominantPrakriti', 'dominantVikriti', 'completedAt'
        ]
        list_fields = [
            'id', 'createdAt', 'updatedAt', 'dominantPrakriti', 'dominantVikriti'
        ]
        read_only_fields = ['id', 'userId', 'completedAt', 'createdAt', 'updatedAt']
