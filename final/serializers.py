from rest_framework import serializers
from .models import Question, Choice, KeywordQuestion, KeywordAnswer


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


class KeywordQuestionDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = KeywordQuestion
        fields = [
            'question_id',
            'question_text',
            'image_url',
            'keyword',
            'order',
        ]

    def image_url(self, user):
        return '/media/' + str(user.image.source)  if user.image is not None else None


class KeywordAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordAnswer
        fields = [
            'team_id',
            'answer',
            'question_id',
        ]
