import json
from datetime import datetime

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
        receiver = text_data_json['receiver']
        sender = text_data_json['sender']
        board = text_data_json['board']
        notification = text_data_json['notification']

        created_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')

        event = {
            'type': 'send_notification',
            'sender': sender,
            'receiver': receiver,
            'board': board,
            'created_at': created_at,
            'notification': notification
        }

        # send message to group
        await self.channel_layer.group_send(self.group_name, event)

    # Receive message from group
    async def send_notification(self, event):

        # 테이블에 데이터 추가
        receiver = await sync_to_async(User.objects.get, thread_sensitive=True)(id=event['receiver'])
        sender = await sync_to_async(User.objects.get, thread_sensitive=True)(id=event['sender'])
        board = await sync_to_async(Board.objects.get, thread_sensitive=True)(id=event['board'])
        notification = f"{sender} 님이 {board.name} 보드에 회원님을 초대했습니다."

        await sync_to_async(Notification.objects.create, thread_sensitive=True)(receiver=receiver,
                                                                                sender=sender,
                                                                                board=board,
                                                                                notification=notification)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "sender": event['sender'],
            "receiver": event['receiver'],
            "board": event['board'],
            "created_at": event['created_at'],
            "notification": event['notification']
        }))
