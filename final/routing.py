from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/team/$", consumers.TeamConsumer.as_asgi()),
    re_path(r"ws/admin/$", consumers.AdminConsumer.as_asgi()),
]
