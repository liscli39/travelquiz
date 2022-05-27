import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class GroupConsumer(WebsocketConsumer):
    def connect(self):
        if not self.scope['user'] or self.scope['user'] is None:
            self.close()

        self.group_id = self.scope['url_route']['kwargs']['group_id']
        async_to_sync(self.channel_layer.group_add)(
            self.group_id,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_id,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        try:
            method = data['method']
            args = data['args']

            if method in dir(self.__class__):
                async_to_sync(self.channel_layer.group_send)(
                    self.group_id,
                    {
                        'type': method,
                        'args': args
                    }
                )
            else:
                self.send(text_data=json.dumps({'error': 'Method not exist.'}))

        except Exception as e:
            self.send(text_data=json.dumps(
                {'error': 'Wrong format or something broken!!'}
            ))

    def join_room(self, event):
        self.send(text_data=json.dumps({
            'event': 'join_room',
        }))
