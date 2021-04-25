from chat import consumers

from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path


websocket_urlpatterns = [
    url(r'^ws$', consumers.ChatConsumer.as_asgi()),
]
