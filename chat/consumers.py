
# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from frontend.utils.auth import get_user_from_token, is_authenticated
from rest_framework.authtoken.models import Token


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['user']
        print('user id')
        print(user_id)
        self.group_name = "{}".format(user_id)
        # Join room group

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None,bytes_data = None):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'recieve_group_message',
                'message': message
            }
        )

    async def recieve_group_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))