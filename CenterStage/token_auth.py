from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from frontend.utils.auth import get_user_from_token, is_authenticated
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

@database_sync_to_async
def get_user(token_key):
    try:
        user_id = Token.objects.get(key=token_key).user_id
        return user_id
    except Token.DoesNotExist:
        return AnonymousUser()

# @sync_to_async
# def get_user(token):
#     user = Token.objects.get(token)
#     return user

class TokenAuthMiddleware(BaseMiddleware):
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner


    async def __call__(self, scope,  receive, send):
        query = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
        token_key = query.get('token')
        print(token_key)
        scope['user'] = await get_user(token_key)
        print(scope['user'])
        return await super().__call__(scope, receive, send)

# TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))