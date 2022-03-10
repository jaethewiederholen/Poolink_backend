from poolink_backend.apps.notification.models import Notification
from poolink_backend.bases.api.serializers import ModelSerializer


class UserNotificationSerializer(ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
