from rest_framework import serializers

from poolink_backend.apps.notification.models import Notification


class UserNotificationSerializer(serializers.Serializer):

    receiver = serializers.IntegerField()
    sender = serializers.IntegerField()
    board = serializers.IntegerField()

    class Meta:
        model = Notification
        fields = '__all__'
