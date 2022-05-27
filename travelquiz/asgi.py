import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async

from django.core.asgi import get_asgi_application
from django.contrib.auth.models import AnonymousUser

from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
import app.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

@database_sync_to_async
def get_user(token):
    print('get_userget_userget_user')
    serializer = VerifyJSONWebTokenSerializer(data={"token": token})
    if serializer.is_valid():
        return serializer.object.get('user') or request.user
    else:
        return None

class QueryAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope['user'] = await get_user(scope["query_string"].decode("utf-8"))
        return await self.app(scope, receive, send)

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": QueryAuthMiddleware(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
})
