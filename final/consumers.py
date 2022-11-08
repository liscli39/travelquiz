import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from threading import Timer

from .models import Team, Question, KeywordQuestion, KeywordAnswer
from .serializers import QuestionDetailSerializer, KeywordQuestionDetailSerializer, KeywordAnswerSerializer

GROUP_NAME = 'final_game'

GS_WAIT = 0
GS_STARTING = 1
QUESTION_POINT = 15

TYPE_RESPONSE = 'send_response'
# Turn 1
TYPE_GET_QUESTIONS = 'get_questions'
TYPE_START_QUESTION = 'start_question'
TYPE_RING_BELL = 'ring_bell'
TYPE_TIMEOUT = 'timeout'
TYPE_ANSWER_QUESTION = 'answer_question'
# Turn 2
TYPE_GET_KQUESTIONS = 'get_kquestions'
TYPE_START_KQUESTION = 'start_kquestion'
TYPE_ANSWER_KQUESTION = 'answer_kquestion'
TYPE_ANSWER_KEYWORD = 'answer_keyword'
TYPE_ANSWERS_LIST = 'answers_list'

ONLY_ACTIONS = [
    'login',
    TYPE_GET_QUESTIONS,
    TYPE_ANSWER_QUESTION,
    TYPE_GET_KQUESTIONS,
]

class BaseConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(GROUP_NAME, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard(
            GROUP_NAME,
            self.channel_name
        ))

    def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] in ONLY_ACTIONS:
            async_to_sync(self.channel_layer.send)(self.channel_name, data)
        else:
            async_to_sync(self.channel_layer.group_send)(GROUP_NAME, data)

    def response(self, event, data):
        self.send(text_data=json.dumps({
            'seq': event['seq'],
            'type': TYPE_RESPONSE,
            'data': data
        }))

class TeamConsumer(BaseConsumer):
    def login(self, event):
        data = event['args']
        team = Team.objects.filter(team_id=data['team_id']).first()
        if team is not None:
            self.scope['team'] = team

        self.response(event, {
            'team_id': team.team_id,
            'role': 'team',
        })

    def start_question(self, event):
        data = event['args']
        question = Question.objects.filter(question_id=data['question_id']).first()

        self.send(text_data=json.dumps({
            'type': event['type'],
            'data': QuestionDetailSerializer(question).data
        }))

    def ring_bell(self, event):
        pass

    def answer_question(self, event):
        pass

    def start_kquestion(self, event):
        data = event['args']
        question = KeywordQuestion.objects.filter(question_id=data['question_id']).first()

        self.send(text_data=json.dumps({
            'type': event['type'],
            'data': KeywordQuestionDetailSerializer(question).data
        }))

    def answer_kquestion(self, event):
        data = event['args']
        team = Team.objects.filter(team_id=data['team_id']).first()
        team.point += QUESTION_POINT
        team.save()

        self.send(text_data=json.dumps({
            'type': TYPE_ANSWER_QUESTION,
            'data': {
                'team_id': data['team_id'],
                'team_point': team.point,
            }
        }))


class AdminConsumer(BaseConsumer):
    flag = None

    def get_questions(self, event):
        data = event['args']
        questions = Question.objects.filter()

        self.response(event, QuestionDetailSerializer(questions, many=True).data)

    def start_question(self, event):
        def timeover():
            self.send(text_data=json.dumps({
                'type': TYPE_TIMEOUT,
                'data': 1
            }))

        t = Timer(5, timeover)
        t.start()

    def ring_bell(self, event):
        data = event['args']
        if self.flag is None:
            self.flag = data["team_id"]
            self.send(text_data=json.dumps({
                'type': event['type'],
                'data': data
            }))

    def answer_question(self, event):
        data = event['args']
        team = Team.objects.filter(team_id=data['team_id']).first()
        team.point += QUESTION_POINT
        team.save()

        self.send(text_data=json.dumps({
            'type': TYPE_ANSWER_QUESTION,
            'data': {
                'team_id': data['team_id'],
                'team_point': team.point,
            }
        }))

    def get_kquestions(self, event):
        data = event['args']
        questions = KeywordQuestion.objects.filter()

        self.response(event, KeywordQuestionDetailSerializer(questions, many=True).data)

    def start_kquestion(self, event):
        question = KeywordQuestion.objects.filter(question_id=data['question_id']).first()

        def timeover():
            answers = KeywordAnswer.objects.filter(question_id=data['question_id'])
            self.send(text_data=json.dumps({
                'type': TYPE_ANSWERS_LIST,
                'data': KeywordAnswerSerializer(answers, many=True).data
            }))

        t = Timer(5, timeover)
        t.start()

