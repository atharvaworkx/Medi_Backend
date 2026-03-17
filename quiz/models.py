from django.db import models
from django.utils.translation import gettext_lazy as _
from atomicloops.models import AtomicBaseModel
from users.models import Users


QUESTION_TYPE_CHOICES = (
    ('yesNo', 'Yes/No'),
    ('multipleChoice', 'Multiple Choice'),
    ('scale', 'Scale (1-5)'),
)


class QuizQuestion(AtomicBaseModel):
    questionText = models.TextField(
        verbose_name=_('Question'),
        db_column='question_text'
    )
    questionType = models.CharField(
        verbose_name=_('Question Type'),
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        db_column='question_type'
    )
    category = models.CharField(
        verbose_name=_('Category'),
        max_length=50,
        db_column='category',
        help_text='e.g., prakriti, vikriti, lifestyle'
    )
    order = models.IntegerField(
        verbose_name=_('Order'),
        db_column='order'
    )
    isActive = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )

    class Meta:
        db_table = 'quiz_questions'
        verbose_name_plural = 'quiz_questions'
        managed = True
        ordering = ['order']

    def __str__(self):
        return f"{self.category} - {self.questionText[:50]}"


class QuizOption(AtomicBaseModel):
    questionId = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        db_column='question_id',
        verbose_name=_('Question')
    )
    optionText = models.CharField(
        verbose_name=_('Option Text'),
        max_length=255,
        db_column='option_text'
    )
    optionValue = models.CharField(
        verbose_name=_('Option Value'),
        max_length=50,
        db_column='option_value',
        help_text='Internal value for scoring'
    )
    scoreData = models.JSONField(
        verbose_name=_('Score Data'),
        default=dict,
        db_column='score_data',
        help_text='Dosha weightage: {vata: 0.5, pitta: 0.3, kapha: 0.2}'
    )
    order = models.IntegerField(
        verbose_name=_('Order'),
        db_column='order'
    )

    class Meta:
        db_table = 'quiz_options'
        verbose_name_plural = 'quiz_options'
        managed = True
        ordering = ['order']

    def __str__(self):
        return f"{self.optionText}"


class QuizResponse(AtomicBaseModel):
    userId = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='quizResponses',
        db_column='user_id',
        verbose_name=_('User')
    )
    questionId = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        db_column='question_id',
        verbose_name=_('Question')
    )
    selectedOptionId = models.ForeignKey(
        QuizOption,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responses',
        db_column='selected_option_id',
        verbose_name=_('Selected Option')
    )
    responseValue = models.CharField(
        verbose_name=_('Response Value'),
        max_length=255,
        db_column='response_value'
    )

    class Meta:
        db_table = 'quiz_responses'
        verbose_name_plural = 'quiz_responses'
        managed = True
        unique_together = ('userId', 'questionId')

    def __str__(self):
        return f"{self.userId.email} - Q{self.questionId.id}"


class QuizResult(AtomicBaseModel):
    userId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='quizResult',
        db_column='user_id',
        verbose_name=_('User')
    )
    prakritScores = models.JSONField(
        verbose_name=_('Prakriti Scores'),
        default=dict,
        db_column='prakriti_scores',
        help_text='{vata: %, pitta: %, kapha: %}'
    )
    vikritScores = models.JSONField(
        verbose_name=_('Vikriti Scores'),
        default=dict,
        db_column='vikriti_scores',
        help_text='{vata: %, pitta: %, kapha: %}'
    )
    dominantPrakriti = models.CharField(
        verbose_name=_('Dominant Prakriti'),
        max_length=20,
        db_column='dominant_prakriti',
        null=True
    )
    dominantVikriti = models.CharField(
        verbose_name=_('Dominant Vikriti'),
        max_length=20,
        db_column='dominant_vikriti',
        null=True
    )
    completedAt = models.DateTimeField(
        verbose_name=_('Completed At'),
        auto_now_add=True,
        db_column='completed_at'
    )

    class Meta:
        db_table = 'quiz_results'
        verbose_name_plural = 'quiz_results'
        managed = True

    def __str__(self):
        return f"Quiz Result - {self.userId.email}"
