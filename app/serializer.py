
from rest_framework import serializers
from app.models import User, Question, Answer, Choice
from app.utils.encryptor import PrimaryKeyEncryptor


class PrimaryHashField(serializers.IntegerField):
    def to_representation(self, value):
        return PrimaryKeyEncryptor().encrypt(value)


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(phone=data['phone']).first()
        if user is None or not user.check_password(data['password']):
            raise serializers.ValidationError()
        return data


class RegisterSerializer(serializers.Serializer):
    phone = serializers.RegexField('^([0-9]{1,12})$')
    name = serializers.CharField()
    address = serializers.CharField()
    office = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(phone=data['phone']).first()
        if user is not None:
            raise serializers.ValidationError()

        return data


class ChoiceSerializer(serializers.ModelSerializer):
    choice_id = PrimaryHashField()

    class Meta:
        model = Choice
        fields = [
            'choice_id',
            'choice_text',
        ]


class QuestionSerializer(serializers.ModelSerializer):
    question_id = PrimaryHashField()
    answered = serializers.BooleanField()

    class Meta:
        model = Question
        fields = [
            'question_id',
            'answered',
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    question_id = PrimaryHashField()
    choices = ChoiceSerializer(many=True, source='choice_set')
    answered = serializers.BooleanField()

    class Meta:
        model = Question
        fields = [
            'question_id',
            'question_text',
            'answered',
            'choices',
        ]

class AnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class RankSerializer(serializers.ModelSerializer):
    corrects = serializers.IntegerField()
    time = serializers.IntegerField()

    class Meta:
        model = User
        fields = [
            'name',
            'phone',
            'corrects',
            'time',
        ]

    def to_representation(self, instance):
        if instance.corrects is None:
            instance.corrects = 0

        if instance.time is None:
            instance.time = 0

        return super().to_representation(instance)