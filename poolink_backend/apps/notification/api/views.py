from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.notification.models import Notification
from poolink_backend.apps.users.models import User
from poolink_backend.bases.api.paginations import SmallResultsSetPagination
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.viewsets import ModelViewSet

from .serializers import UserNotificationSerializer


class NotificationViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = UserNotificationSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Notification.objects.all()

    @swagger_auto_schema(
        operation_id=_("리스트조회"),
        operation_description=_("모든 알림 내역을 조회합니다."),
        responses={200: openapi.Response(_("OK"), UserNotificationSerializer)},
        manual_parameters=[
            openapi.Parameter('shared', openapi.IN_QUERY, type='boolean')],
    )
    def list(self, request):
        paginator = SmallResultsSetPagination()
        notifications = Notification.objects.all()
        page = paginator.paginate_queryset(notifications, request)
        serializer = UserNotificationSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # def get_queryset(self, *args, **kwargs):
    #     try:
    #         receiver = self.lookup_url_kwarg['receiver']
    #         if receiver:
    #             user_obj = User.objects.get(id=receiver)
    #             if user_obj:
    #                 return Notification.objects.filter(user=user_obj)
    #     except ObjectDoesNotExist:
    #         return Response(status=HTTP_404_NOT_FOUND,
    #                         data=MessageSerializer({"message": _("존재하지 않는 유저입니다.")}).data)

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
                                             notification=f"{sender} 님이 {board.name} 보드에 회원님을 초대했습니다.")

        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _(result.notification)}).data)
