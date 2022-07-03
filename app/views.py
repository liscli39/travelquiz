from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken

from django.db.models import OuterRef, Count, Exists, Sum
from django.shortcuts import render

from app.models import User, Question, Answer, Group, GroupUser, GroupAnswer, Week
from app.serializer import LoginSerializer, RegisterSerializer, QuestionDetailSerializer, QuestionSerializer, \
    AnswerQuestionSerializer, RankSerializer, GroupSerializer, GroupUserSerializer, GroupAnswerSerializer, UserSerializer, \
    WeekSerializer
from app.utils.encryptor import PrimaryKeyEncryptor
from app.utils.enum import Enum
from app.utils.common import send_to_channel_room

from threading import Timer
from datetime import datetime


def index(request):
    return render(request, 'index.html')

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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data

        week = Week.objects.filter(is_active=True).first()
        data['week'] = week.name if week else None

        return Response(data)


class QuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = Question.objects.filter(week__is_active=True)

        serializer = QuestionDetailSerializer(questions, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = [{
            'user': user.user_id,
            **choice,
        } for choice in request.data]

        serializer = AnswerQuestionSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(data, status=status.HTTP_200_OK)



class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
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
        question = Question.objects.filter(question_id=question_id).first()

        if Answer.objects.filter(user=user, question_id=question_id).exists():
            return Response({'error': 'QUESTION_ALREADY_SUBMIT'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user': user.user_id,
            'question': question_id,
        }

        if 'choice_id' in request.data:
            data['choice'] = request.data['choice_id']
        
        data['time'] = request.data['time'] if 'time' in request.data else 9999

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

        corrects = Question.objects.filter(week__is_active=True, question_id__in=answers.filter(choice__is_correct=True, question__isnull=False)
                                           .values_list('question_id', flat=True))

        total = Question.objects.filter(week__is_active=True, question_id__in=answers.values_list('question_id', flat=True))

        total_time = answers.filter(question__week__is_active=True).aggregate(Sum('time'))['time__sum']

        current = datetime.now()
        startday = current.replace(hour=0, minute=0, second=0, microsecond=0)

        times = user.resets.split(';') if user.resets is not None else []
        times = [x for x in times if datetime.fromtimestamp(int(x)) > startday][:3]

        result = {
            "corrects": corrects.count(),
            "total": total.count(),
            "reset_time": len(times),
            "total_time": total_time,
        }

        return Response({'result': result})

    def delete(self, request):
        user = request.user
        current = datetime.now()
        startday = current.replace(hour=0, minute=0, second=0, microsecond=0)

        times = user.resets.split(';') if user.resets is not None else []
        times = [x for x in times if datetime.fromtimestamp(int(x)) > startday][:3]

        if len(times) > 2:
            return Response({'error': 'RESET_LIMIT'}, status=status.HTTP_400_BAD_REQUEST)

        Answer.objects.filter(user=user, question__week__is_active=True).delete()

        times.append(str(int(current.timestamp())))
        user.resets = ';'.join(times)
        user.save()

        return Response({'result': 'ok'})


class RankView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        completed = Answer.objects.values('user_id').annotate(question_count=Count('question_id'))\
            .filter(question_count=Question.objects.filter(week__is_active=True).count()).values_list('user_id', flat=True)

        users = User.objects.raw('''
            SELECT
                `app_user`.`user_id`,
                `app_user`.`phone`,
                `app_user`.`name`,
                (
                SELECT COUNT(V0.`question_id`) AS `count`
                FROM `app_question` V0
                WHERE V0.`question_id` IN(
                    SELECT U0.`question_id`
                    FROM `app_answer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE  U1.`is_correct` AND U0.`question_id` IS NOT NULL AND U0.`user_id` = `app_user`.`user_id`
                ) LIMIT 1
                ) AS `corrects`,
                (
                    SELECT SUM(U0.`time`)
                    FROM `app_answer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE U1.`is_correct` AND U0.`question_id` IS NOT NULL AND U0.`user_id` = `app_user`.`user_id`
                    GROUP BY U0.`user_id`
                    ORDER BY NULL
                    LIMIT 1
                ) AS `time`
            FROM `app_user`
            WHERE NOT `app_user`.`is_superuser` AND
                `app_user`.`user_id` IN ({}) AND (
                SELECT COUNT(V0.`question_id`) AS `count`
                FROM `app_question` V0
                WHERE V0.`question_id` IN(
                    SELECT U0.`question_id`
                    FROM `app_answer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE  U1.`is_correct` AND U0.`question_id` IS NOT NULL AND U0.`user_id` = `app_user`.`user_id`
                ) LIMIT 1
            ) > 0
            ORDER BY `corrects` DESC, `time` ASC;
        '''.format(completed.query))
        
        serializer = RankSerializer(users, many=True)

        return Response({'result': serializer.data})


class GroupView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        if Group.objects.filter(created_by=user).exists():
            # return Response({'error': 'USER_ALREADY_GROUP_OWNER'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = GroupSerializer(Group.objects.filter(created_by=user).first())
        else:
            data = {
                'group_title': request.data['group_title'],
                'created_by': user.user_id,
            }

            serializer = GroupSerializer(data=data)
            if not serializer.is_valid():
                return Response({'error': 'INVALID_PARAMS'}, status=status.HTTP_400_BAD_REQUEST)

            group = serializer.save()
            # Wait for 15 minutes before cancel group
            Timer(900, self.timeout_handle, (group.group_id,)).start()

        data = serializer.data
        return Response(data)

    def timeout_handle(self, group_id):
        group = Group.objects.filter(group_id=group_id).first()
        if group is None:
            return
        
        if group.status == Enum.GROUP_STATUS_WAITING:
            serializer = GroupSerializer(group)
            data = serializer.data

            send_to_channel_room(data['group_id'], 'cancel_room', 0)
            GroupUser.objects.filter(group=group).delete()
            group.delete()


class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        group = Group.objects.filter(group_id=group_id).first()
        if group is None:
            return Response({'error': 'GROUP_DOES_NOT_EXIST'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = GroupSerializer(group)
        data = serializer.data

        return Response(data)

    def delete(self, request, group_id):
        group = Group.objects.filter(group_id=group_id).first()
        if group is None:
            return Response({'error': 'GROUP_DOES_NOT_EXIST'}, status=status.HTTP_400_BAD_REQUEST)

        if group.created_by_id != request.user.user_id:
            return Response({'error': 'NOT_OWNER_GROUP'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GroupSerializer(group)
        data = serializer.data

        send_to_channel_room(data['group_id'], 'cancel_room', 0)
        GroupUser.objects.filter(group=group).delete()
        group.delete()

        return Response({"result": "ok"})

    def put(self, request, group_id):
        group = Group.objects.filter(group_id=group_id).first()
        if group is None:
            return Response({'error': 'GROUP_DOES_NOT_EXIST'}, status=status.HTTP_400_BAD_REQUEST)

        if group.created_by_id != request.user.user_id:
            return Response({'error': 'NOT_OWNER_GROUP'}, status=status.HTTP_400_BAD_REQUEST)

        if GroupUser.objects.filter(group=group, status=Enum.USER_GROUP_STATUS_READY).count() < Enum.MIN_JOIN_MEMBER:
            return Response({'error': 'NOT_ENOUGH_READY'}, status=status.HTTP_400_BAD_REQUEST)

        not_ready = GroupUser.objects.filter(group=group).exclude(status=Enum.USER_GROUP_STATUS_READY)
        not_ready_list = list(not_ready.values_list('user_id', flat=True))
        not_ready.delete()

        group.status = Enum.GROUP_STATUS_PLAYING
        group.save()

        GroupUser.objects.filter(group=group, status=Enum.USER_GROUP_STATUS_READY) \
            .update(status=Enum.USER_GROUP_STATUS_INGAME)

        send_to_channel_room(group_id, 'game_start', not_ready_list)
        return Response({"result": "ok"})


class GroupJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        user = request.user

        serializer = GroupUserSerializer(data={
            'group': group_id,
            'user': user.user_id,
            'status': Enum.USER_GROUP_STATUS_WAITING 
        })

        if not serializer.is_valid():
            print(serializer.errors)
            return Response({'error': 'INVALID_PARAMS'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()  
        send_to_channel_room(group_id, 'join_room', user.user_id)

        return Response({"result": "ok"})


class GroupReadyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        user = request.user
        group_user = GroupUser.objects.filter(user=user, group_id=group_id).first()

        if group_user is None:
            return Response({'error': 'NOT_JOIN_YET'}, status=status.HTTP_400_BAD_REQUEST)

        if group_user.status != Enum.USER_GROUP_STATUS_WAITING:
            return Response({'error': 'ALREADY_READY'}, status=status.HTTP_400_BAD_REQUEST)

        group_user.status = Enum.USER_GROUP_STATUS_READY
        group_user.save()
        send_to_channel_room(group_id, 'ready_play', user.user_id)

        return Response({"result": "ok"})


class GroupQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        user = request.user

        answer = GroupAnswer.objects.filter(group_id=group_id, user=user, question_id=OuterRef('question_id'))
        questions = Question.objects.all().annotate(answered=Exists(answer)).order_by('?')

        serializer = QuestionSerializer(questions, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)


class GroupQuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id, question_id):
        user = request.user

        answer = GroupAnswer.objects.filter(group_id=group_id, user=user, question_id=OuterRef('question_id'))
        question = Question.objects.filter(question_id=question_id)\
            .annotate(answered=Exists(answer)).first()

        if question is None:
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuestionDetailSerializer(question)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, group_id, question_id):
        user = request.user
        group = Group.objects.filter(group_id=group_id).first()

        if group is None:
            return Response({'error': 'GROUP_NOT_EXIST'}, status=status.HTTP_400_BAD_REQUEST)

        group_user = GroupUser.objects.filter(group_id=group.group_id, user_id=user.user_id, 
                                              status=Enum.USER_GROUP_STATUS_INGAME).first()
        if group_user is None:
            return Response({'error': 'USER_NOT_INGAME'}, status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.filter(question_id=question_id).first()
        if GroupAnswer.objects.filter(group_id=group.group_id, user_id=user.user_id, question_id=question_id).exists():
            return Response({'error': 'QUESTION_ALREADY_SUBMIT'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'group': group.group_id,
            'user': user.user_id,
            'question': question_id,
        }

        if 'choice' in request.data:
            data['choice'] = request.data['choice']
        
        if 'time' in request.data:
            data['time'] = request.data['time']

        serializer = GroupAnswerSerializer(data=data)

        if question is None or not serializer.is_valid():
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        
        # Check finish
        all_questions_count = Question.objects.count()
        user_answer_count = GroupAnswer.objects.filter(group_id=group.group_id, user=user.user_id).count()
        if user_answer_count >= all_questions_count:
            group_user.status = Enum.USER_GROUP_STATUS_FINISHED
            group_user.save()

        # Check all finish
        group_user_count = GroupUser.objects.filter(group_id=group.group_id).count()
        completed_count = GroupAnswer.objects.values('user_id').annotate(question_count=Count('question_id'))\
            .filter(group_id=group.group_id, question_count=all_questions_count).count()
        
        if completed_count >= group_user_count:
            group.status = Enum.GROUP_STATUS_FINISHED
            group.save()
            send_to_channel_room(group_id, 'gameover', 0)

        return Response({'result': 'ok'},  status=status.HTTP_200_OK)


class GroupAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        user = request.user
        answers = GroupAnswer.objects.filter(group_id=group_id, user_id=user.user_id)

        corrects = Question.objects.filter(question_id__in=answers.filter(choice__is_correct=True, question__isnull=False)
                                           .values_list('question_id', flat=True))

        total = Question.objects.filter(question_id__in=answers.values_list('question_id', flat=True))

        result = {
            "corrects": corrects.count(),
            "total": total.count(),
        }

        return Response({'result': result})


class GroupRankView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        completed = GroupAnswer.objects.values('user_id').annotate(question_count=Count('question_id'))\
            .filter(group_id=group_id, question_count=Question.objects.count()).values_list('user_id', flat=True)

        users = User.objects.raw('''
            SELECT
                `app_user`.`user_id`,
                `app_user`.`phone`,
                `app_user`.`name`,
                (
                SELECT COUNT(V0.`question_id`) AS `count`
                FROM `app_question` V0
                WHERE V0.`question_id` IN(
                    SELECT U0.`question_id`
                    FROM `app_groupanswer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE  U1.`is_correct` 
                        AND U0.`question_id` IS NOT NULL 
                        AND U0.`user_id` = `app_user`.`user_id`
                        AND U0.`group_id` = {group_id}
                ) LIMIT 1
                ) AS `corrects`,
                (
                    SELECT SUM(U0.`time`)
                    FROM `app_groupanswer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE U1.`is_correct` 
                        AND U0.`question_id` IS NOT NULL 
                        AND U0.`user_id` = `app_user`.`user_id`
                        AND U0.`group_id` = {group_id}
                    GROUP BY U0.`user_id`
                    ORDER BY NULL
                    LIMIT 1
                ) AS `time`
            FROM `app_user`
            WHERE NOT `app_user`.`is_superuser` AND
                `app_user`.`user_id` IN ({query}) AND (
                SELECT COUNT(V0.`question_id`) AS `count`
                FROM `app_question` V0
                WHERE V0.`question_id` IN(
                    SELECT U0.`question_id`
                    FROM `app_groupanswer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE  U1.`is_correct` 
                        AND U0.`question_id` IS NOT NULL 
                        AND U0.`user_id` = `app_user`.`user_id`
                        AND U0.`group_id` = {group_id}
                ) LIMIT 1
            ) > 0
            ORDER BY `corrects` DESC, `time` ASC;
        '''.format(query=completed.query, group_id=group_id))
        
        serializer = RankSerializer(users, many=True)

        return Response({'result': serializer.data})


class WeekView(APIView):
    permission_classes = []

    def get(self, request):
        week = Week.objects.filter(is_active=True).first()
        if week is None:
            return Response({'result': None})

        serializer = WeekSerializer(week)
        return Response({'result': serializer.data})
