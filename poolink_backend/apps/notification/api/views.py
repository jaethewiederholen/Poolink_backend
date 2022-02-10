from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.notification.models import Notification
from poolink_backend.apps.users.models import User
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.viewsets import ModelViewSet

from .serializers import UserNotificationSerializer


class NotificationViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = UserNotificationSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Notification.objects.all()

    def get_queryset(self, *args, **kwargs):
        try:
            receiver = self.lookup_url_kwarg['receiver']
            if id:
                user_obj = User.objects.get(id=receiver)
                if user_obj:
                    return Notification.objects.filter(user=user_obj)
        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND,
                            data=MessageSerializer({"message": _("존재하지 않는 유저입니다.")}).data)

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]

        obj = Notification.objects.get(id=lookup_field_value)
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        notification_obj = request.data["notification"]

        receiver = User.objects.get(id=notification_obj["receiver"])
        sender = User.objects.get(id=notification_obj["sender"])
        board = Board.objects.get(id=notification_obj["board"])

        result = Notification.objects.create(receiver=receiver, sender=sender, board=board,
                                             notification=f"{sender}가 {board.name}에 초대했습니다.")

        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _(result.notification)}).data)
