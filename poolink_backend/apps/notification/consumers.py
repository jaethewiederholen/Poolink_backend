import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.notification.models import Notification
from poolink_backend.apps.users.models import User


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = 'notification'

        # join to group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self):
        # leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        notification = text_data_json['notification']

        event = {
            'type': 'send_notification',
            'notification': notification
        }

        # send message to group
        await self.channel_layer.group_send(self.group_name, event)

    # Receive message from group
    async def send_notification(self, event):

        # view 에 작성한 코드와 동일 -- 동작 방식 다시 확인해보자
        notification_obj = json.loads(json.dumps(event['notification']))

        receiver = await sync_to_async(User.objects.get, thread_sensitive=True)(id=notification_obj['receiver'])
        sender = await sync_to_async(User.objects.get, thread_sensitive=True)(id=notification_obj['sender'])
        board = await sync_to_async(Board.objects.get, thread_sensitive=True)(id=notification_obj['board'])
        notification = f"{sender}가 {board.name}에 초대했습니다."

        await sync_to_async(Notification.objects.create, thread_sensitive=True)(receiver=receiver,
                                                                                sender=sender,
                                                                                board=board,
                                                                                notification=notification)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "notification": {
                "receiver": notification_obj['receiver'],
                "sender": notification_obj['sender'],
                "board": notification_obj['board'],
                "notification": notification_obj['notification']
            }
        }))
