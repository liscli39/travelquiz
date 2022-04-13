from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken

from django.db.models import OuterRef, Subquery, Count, Sum

from app.models import User, Question, Choice, Answer
from app.serializer import LoginSerializer, RegisterSerializer, QuestionDetailSerializer, QuestionSerializer, \
    AnswerQuestionSerializer, RankSerializer

from app.utils.encryptor import PrimaryKeyEncryptor


class LoginView(ObtainJSONWebToken):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': 'INVALID_EMAIL_OR_PASSWORD'}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)


class RegisterView(ObtainJSONWebToken):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data
        User.objects.create_user(
            name=data['name'],
            phone=data['phone'],
            address=data['address'],
            office=data['office'],
            password=data['password'],
        )

        return super().post(request, *args, **kwargs)


class QuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)


class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question_id = PrimaryKeyEncryptor().decrypt(question_id)
        question = Question.objects.filter(question_id=question_id).first()

        if question is None:
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuestionDetailSerializer(question)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, question_id):
        user = request.user

        question_id = PrimaryKeyEncryptor().decrypt(question_id)
        question = Question.objects.filter(question_id=question_id).first()

        choice_id = PrimaryKeyEncryptor().decrypt(request.data['choice_id'])
        
        if Answer.objects.filter(choice__question_id=question_id).exists():
            return Response({'error': 'QUESTION_ALREADY_SUBMIT'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AnswerQuestionSerializer(data={
            'user': user.user_id,
            'choice': choice_id,
            'time': request.data['time'],
        })

        if question is None or not serializer.is_valid():
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({'result': 'ok'},  status=status.HTTP_200_OK)


class AnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        answers = Answer.objects.filter(user=user)

        corrects = Question.objects.filter(question_id__in=answers.filter(choice__is_correct=True)
            .values_list('choice__question_id', flat=True))

        total = Question.objects.filter(question_id__in=answers.values_list('choice__question_id', flat=True))

        return Response({
            "corrects": corrects.count(),
            "total": total.count(),
        })


class RankView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        answers = Answer.objects.filter(user_id=OuterRef('user_id'), choice__is_correct=True)

        corrects = Question.objects.annotate(user_id=OuterRef('user_id'))\
            .filter(question_id__in=answers.values_list('choice__question_id', flat=True)) \
            .annotate(question_count=Count('question_id'))

        time_count = answers.annotate(time_count=Sum('time'))

        users = User.objects.filter(is_superuser=False).annotate(
            corrects=Subquery(corrects.values_list('question_count')[:1]),
            time=Subquery(time_count.values_list('time_count')[:1]),
        ).order_by('-corrects', 'time')
        
        serializer = RankSerializer(users, many=True)

        return Response({'result': serializer.data })
