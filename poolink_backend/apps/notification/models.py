import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.utils.translation import ugettext_lazy as _

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.users.api.serializers import UserSerializer
from poolink_backend.apps.users.models import User
from poolink_backend.bases.models import Model

NOTIFICATION_CHOICES = (
    (0, _("초대됨")),
    (1, _("수락")),
    (2, _("거절")),
)


class Notification(Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_notification", null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_notification", null=True)
    notification = models.TextField(max_length=255)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, choices=NOTIFICATION_CHOICES)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        date_time = datetime.now()
        data = {
            "sender": UserSerializer(self.sender).data,
            "notification": self.notification,
            "created": date_time.isoformat()
        }
        async_to_sync(channel_layer.group_send)(
            "test_group", {
                'type': 'send_notification',
                'value': json.dumps(data)
            }
        )
        super(Notification, self).save(*args, **kwargs)

    def get_user_notifications(user):
        user_notifications = Notification.objects.filter(receiver=user)
        return user_notifications
