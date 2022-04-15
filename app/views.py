from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken

from django.db.models import OuterRef, Subquery, Count, Sum, Exists

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
        answer = Answer.objects.filter(question_id=OuterRef('question_id'))
        questions = Question.objects.all().annotate(answered=Exists(answer))

        serializer = QuestionSerializer(questions, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)


class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question_id = PrimaryKeyEncryptor().decrypt(question_id)

        answer = Answer.objects.filter(question_id=OuterRef('question_id'))
        question = Question.objects.filter(question_id=question_id)\
            .annotate(answered=Exists(answer)).first()

        if question is None:
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuestionDetailSerializer(question)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, question_id):
        user = request.user

        question_id = PrimaryKeyEncryptor().decrypt(question_id)
        question = Question.objects.filter(question_id=question_id).first()

        if Answer.objects.filter(user=user, question_id=question_id).exists():
            return Response({'error': 'QUESTION_ALREADY_SUBMIT'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user': user.user_id,
            'question': question_id,
        }

        if 'choice_id' in request.data:
            data['choice'] = PrimaryKeyEncryptor().decrypt(request.data['choice_id'])
        
        if 'time' in request.data:
            data['time'] = request.data['time']

        serializer = AnswerQuestionSerializer(data=data)

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
                                           .values_list('question_id', flat=True)).values_list('question_id', flat=True)

        total = Question.objects.filter(question_id__in=answers.values_list('question_id', flat=True))

        result = {
            "corrects": [PrimaryKeyEncryptor().encrypt(correct) for correct in corrects],
            "total": total.count(),
        }

        return Response({'result': result})


class RankView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        answers = Answer.objects.filter(
            user_id=OuterRef('user_id'), choice__is_correct=True, question__isnull=False)

        corrects = Question.objects.annotate(user_id=OuterRef('user_id'))\
            .filter(question_id__in=answers.values_list('question_id', flat=True)) \
            .annotate(question_count=Count('question_id'))

        time_count = answers.annotate(time_count=Sum('time'))

        users = User.objects.filter(is_superuser=False).annotate(
            corrects=Subquery(corrects.values_list('question_count')[:1]),
            time=Subquery(time_count.values_list('time_count')[:1]),
        ).order_by('-corrects', 'time')

        serializer = RankSerializer(users, many=True)

        return Response({'result': serializer.data})
