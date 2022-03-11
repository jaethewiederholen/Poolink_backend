from rest_framework import serializers

from poolink_backend.apps.notification.models import Notification
from poolink_backend.bases.api.serializers import ModelSerializer


class UserNotificationSerializer(ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'board', 'notification', 'created']


class NotificationCheckSerializer(serializers.Serializer):

    check = serializers.IntegerField()
