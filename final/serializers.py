from rest_framework import serializers
from .models import Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = [
            'choice_id',
            'choice_text',
            'is_correct',
        ]

class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, source='choice_set')

    class Meta:
        model = Question
        fields = [
            'question_id',
            'question_text',
            'choices',
        ]
