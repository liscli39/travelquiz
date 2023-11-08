
from rest_framework import serializers
from app.models import User, Question, Answer, Choice, Group, GroupUser, GroupAnswer, Week, Island, Rank
from app.utils.encryptor import PrimaryKeyEncryptor
from app.utils.enum import Enum


class PrimaryHashField(serializers.IntegerField):
    def to_representation(self, value):
        return PrimaryKeyEncryptor().encrypt(value)


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(phone=data['phone']).first()
        if user is None or not user.check_password(data['password']) or not user.allow_access:
            raise serializers.ValidationError()
        return data

class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(phone=data['phone']).first()
        if user is None or not user.allow_access:
            raise serializers.ValidationError()
        return data

class RegisterSerializer(serializers.Serializer):
    phone = serializers.RegexField('^([0-9]{1,12})$')
    name = serializers.CharField()
    gender = serializers.IntegerField()
    job = serializers.CharField()
    office = serializers.CharField()
    password = serializers.CharField()
    prefecture = serializers.CharField()
    district = serializers.CharField()
    wards = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(phone=data['phone']).first()
        if user is not None:
            raise serializers.ValidationError()

        return data


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = [
            'choice_id',
            'choice_text',
            'is_correct',
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answered = serializers.BooleanField()

    class Meta:
        model = Question
        fields = [
            'question_id',
            'answered',
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, source='choice_set')
    week_name = serializers.CharField(source='week')

    class Meta:
        model = Question
        fields = [
            'question_id',
            'question_text',
            'choices',
            'wiki_url',
            'wiki_title',
            'week_name',
        ]

class AnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class RankSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    phone = serializers.CharField(source='user.phone')
    class Meta:
        model = Rank
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

class GroupUserField(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    phone = serializers.CharField(source='user.phone')
    name = serializers.CharField(source='user.name')
    address = serializers.CharField(source='user.address')
    office = serializers.CharField(source='user.office')

    class Meta:
        model = GroupUser
        fields = [
            'user_id',
            'phone',
            'name',
            'address',
            'office',
            'status',
        ]

class GroupSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    users = GroupUserField(many=True, source='groupuser_set')

    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        validated_data['status'] = Enum.GROUP_STATUS_WAITING
        return super().create(validated_data)


class GroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupUser
        fields = '__all__'


class GroupAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupAnswer
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id',
            'phone',
            'name',
            'address',
            'office',
        ]


class IslandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Island
        fields = ['title', 'descript']


class WeekSerializer(serializers.ModelSerializer):
    islands = IslandSerializer(many=True, source='island_set')

    class Meta:
        model = Week
        fields = ['name', 'is_active', 'limit_time', 'limit_question', 'islands']
