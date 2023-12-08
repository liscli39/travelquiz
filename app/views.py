from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken

from django.db.models import OuterRef, Count, Exists, Sum, Q
from django.shortcuts import render

from app.models import User, Question, Answer, Group, GroupUser, GroupAnswer, Week, Rank, Chart
from app.serializer import LoginSerializer, RegisterSerializer, QuestionDetailSerializer, QuestionSerializer, \
    AnswerQuestionSerializer, RankSerializer, GroupSerializer, GroupUserSerializer, GroupAnswerSerializer, UserSerializer, \
    WeekSerializer, PhoneSerializer

from app.utils.enum import Enum

from threading import Timer
from datetime import datetime, timedelta
import pytz


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
            gender=data['gender'],
            office=data['office'],
            job=data['job'],
            password=data['password'],
            raw_password=data['password'],
            prefecture=data['prefecture'],
            district=data['district'],
            wards=data['wards'],
            year=data['year'],
            cccd=data['cccd'],
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


class PasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PhoneSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': 'INVALID_PHONE'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=serializer.data['phone']).first()
        
        return Response({'result': user.raw_password},  status=status.HTTP_200_OK)

class QuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = Question.objects.select_related('week').prefetch_related('choice_set') \
            .filter(week__is_active=True)

        serializer = QuestionDetailSerializer(questions, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        current = datetime.now()
        turn = str(int(current.timestamp()))
        data = [{
            'user': user.user_id,
            'turn': turn,
            **choice,
        } for choice in request.data]

        serializer = AnswerQuestionSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)
        
        # time_sum = 0
        # for answer in serializer.data:
        #     time_sum += answer['time']
        
        # if time_sum < 1500:
        #     return Response({'error': 'INVALID_INPUT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        startday = current.replace(hour=0, minute=0, second=0, microsecond=0)
        startday = startday - timedelta(days=startday.weekday())

        times = user.resets.split(';') if user.resets is not None else []
        times = [x for x in times if datetime.fromtimestamp(int(x)) > startday][:3]

        if len(times) > 1:
            return Response({'error': 'RESET_LIMIT'}, status=status.HTTP_400_BAD_REQUEST)

        times.append(turn)
        user.resets = ';'.join(times)
        user.save()

        answers = serializer.save()
        for answer in answers:
            answer.is_correct = answer.choice.is_correct if answer.choice else None
            answer.save()

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

        times = user.resets.split(';') if user.resets is not None else []
        data = {
            'user': user.user_id,
            'question': question_id,
            'turn': times[-1]
        }

        if 'choice_id' in request.data:
            data['choice'] = request.data['choice_id']
        
        if 'content' in request.data:
            data['content'] = request.data['content']

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
        times = user.resets.split(';') if user.resets is not None else [0]

        answers = Answer.objects.filter(user=user, turn=times[-1])

        corrects = Question.objects.filter(week__is_active=True, question_id__in=answers.filter(is_correct=True, question__isnull=False)
                                           .values_list('question_id', flat=True))

        total = Question.objects.filter(week__is_active=True, question_id__in=answers.values_list('question_id', flat=True))

        total_time = answers.filter(question__week__is_active=True).aggregate(Sum('time'))['time__sum']

        current = datetime.now()
        startday = current.replace(hour=0, minute=0, second=0, microsecond=0)
        startday = startday - timedelta(days=startday.weekday())

        predict_answer = Answer.objects.filter(user=user, turn=times[-1], question__week__is_active=True, question__type=Enum.QUESTION_PREDICT).first()
        result = {
            "corrects": corrects.count(),
            "total": total.count(),
            "predict": predict_answer.content if predict_answer is not None else 0,
            "reset_time": len(times) - 1,
            "total_time": total_time,
        }

        return Response({'result': result})

    def delete(self, request):
        user = request.user
        current = datetime.now()
        startday = current.replace(hour=0, minute=0, second=0, microsecond=0)
        startday = startday - timedelta(days=startday.weekday())

        times = user.resets.split(';') if user.resets is not None else []
        times = [x for x in times if datetime.fromtimestamp(int(x)) > startday][:3]

        if len(times) > 1:
            return Response({'error': 'RESET_LIMIT'}, status=status.HTTP_400_BAD_REQUEST)

        Answer.objects.filter(Q(question__week__is_active=True) | Q(question=None), user=user).delete()

        times.append(str(int(current.timestamp())))
        user.resets = ';'.join(times)
        user.save()

        return Response({'result': 'ok'})


class RankView(APIView):
    permission_classes = []

    def get(self, request):      
        ranks = Rank.objects.filter(week__show_rank=True, selected=True)
        serializer = RankSerializer(ranks, many=True)

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

        return Response({'result': 'ok'},  status=status.HTTP_200_OK)


class GroupAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        user = request.user
        answers = GroupAnswer.objects.filter(group_id=group_id, user_id=user.user_id)

        corrects = Question.objects.filter(question_id__in=answers.filter(is_correct=True, question__isnull=False)
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

class ChartDataView(APIView):
    permission_classes = []

    def get(self, request):
        # data for user graph
        current = datetime.now()
        start_day = current.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC) - timedelta(days=29)

        user_graph = []
        anwser_graph = []

        user_count = 0
        anwser_count = 0
        anwser_correct = 0

        for day in range(0, 30):
            chart = Chart.objects.filter(date=start_day).first()

            if chart is None:
                user_count += User.objects.filter(date_joined__gte=start_day, date_joined__lt=(start_day + timedelta(days=1))).count()
                anwsers = Answer.objects.filter(answer_at__gte=start_day, answer_at__lt=(start_day + timedelta(days=1)), question__isnull=False)
                anwser_count += anwsers.count()

                corrects = anwsers.filter(is_correct=True).count()
                anwser_correct += corrects
                if current.date() != start_day.date():
                    Chart.objects.create(
                        date=start_day,
                        user_count=user_count,
                        anwser_count=anwser_count,
                        anwser_correct=corrects,
                    )
            else:
                user_count = chart.user_count
                anwser_count = chart.anwser_count
                anwser_correct += chart.anwser_correct

            user_graph.append(user_count)
            anwser_graph.append(anwser_count)
            start_day = start_day + timedelta(days = 1)

        anwser_type_graph = [anwser_correct, anwser_count - anwser_correct]

        prefecture_graph = []
        prefectures = User.objects.filter(date_joined__gte='2023-10-25').values_list('prefecture', flat=True).distinct()
        for prefecture in prefectures:
            prefecture_graph.append(User.objects.filter(prefecture=prefecture).count())

        return Response({'result': {
            'user_graph': user_graph,
            'anwser_graph': anwser_graph,
            'anwser_type_graph': anwser_type_graph,
            'prefecture_graph': prefecture_graph,
            'prefectures': prefectures,
        }}) 