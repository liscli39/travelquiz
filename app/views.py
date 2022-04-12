from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken


from app.models import User, Question, Choice, Answer
from app.serializer import LoginSerializer, RegisterSerializer, QuestionDetailSerializer, QuestionSerializer

from app.utils.encryptor import PrimaryKeyEncryptor

class LoginView(ObtainJSONWebToken):
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({ 'error': 'INVALID_EMAIL_OR_PASSWORD' }, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)


class RegisterView(ObtainJSONWebToken):
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({ 'error': 'INVALID_INPUT_DATA' }, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({ 'error': 'INVALID_INPUT_DATA' }, status=status.HTTP_400_BAD_REQUEST) 

        serializer = QuestionDetailSerializer(question)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request, question_id):
        return Response()


class AnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response()
