import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from threading import Timer

from .models import Team, Question
from .serializers import QuestionDetailSerializer

GROUP_NAME = 'final_game'

GS_WAIT = 0
GS_STARTING = 1

TYPE_RESPONSE = 'send_response'

ONLY_ACTIONS = [
    'room_login',
    'room_get_questions',
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
        data['type'] = 'room_' + str(data['type'])

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
    def room_login(self, event):
        data = event['args']
        team = Team.objects.filter(username=data['username']).first()
        if team is not None:
            self.scope['team'] = team

        self.response(event, {
            'team_id': team.team_id,
            'role': 'team',
        })

    def room_start_question(self, event):
        data = event['args']
        question = Question.objects.filter(question_id=data['question_id']).first()

        self.send(text_data=json.dumps({
            'type': event['type'],
            'data': QuestionDetailSerializer(question).data
        }))

    def room_ring_flag(self, event):
        pass


class AdminConsumer(BaseConsumer):
    game_state = GS_WAIT
    flag = None

    def room_get_questions(self, event):
        data = event['args']
        questions = Question.objects.filter()

        self.response(event, QuestionDetailSerializer(questions, many=True).data)

    def room_start_question(self, event):
        self.game_state = GS_STARTING

        def timeover():
            self.send(text_data=json.dumps({
                'type': 'timeover',
                'data': 1
            }))

        t = Timer(5, timeover)
        t.start()

    def room_ring_flag(self, event):
        data = event['args']
        if self.flag is None:
            self.flag = data["username"]
            self.send(text_data=json.dumps({
                'type': event['type'],
                'data': data
            }))
