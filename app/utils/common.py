import channels.layers
from asgiref.sync import async_to_sync

def send_to_channel_room(room_name, action_type, data):
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(room_name, {
        'type': action_type,
        'data': data,
    })
