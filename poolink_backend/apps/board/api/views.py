from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from poolink_backend.apps.board.api.serializers import (
    BoardDestroySerializer,
    BoardSerializer,
    MyBoardSerializer,
    ScrapBoardSerializer,
)
from poolink_backend.apps.board.models import Board
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    filterset_fields = ["name"]


class MyBoardView(BaseAPIView):
    allowed_method = ("GET", "POST", "DELETE")

    @swagger_auto_schema(
        operation_id=_("Get My Board"),
        operation_description=_("저장 페이지에 보여질 보드들 입니다."),
        responses={200: openapi.Response(_("OK"), MyBoardSerializer,)},
        tags=[_("보드"), ],
    )
    def get(self, request):
        user = self.request.user
        my_board = Board.objects.filter(user_id=user.id)

        return Response(status=HTTP_200_OK, data=MyBoardSerializer(my_board, many=True).data)

    @swagger_auto_schema(
        operation_id=_("Create My Board"),
        operation_description=_("보드를 추가합니다."),
        request_body=MyBoardSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("보드"), ],
    )
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = MyBoardSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_board = serializer.save()
            data = {"id": new_board.id}
            data.update(MessageSerializer({"message": _("보드를 생성했습니다.")}).data)
            return Response(
                status=HTTP_200_OK,
                data=data,
            )

    @swagger_auto_schema(
        operation_id=_("Delete My Board"),
        operation_description=_("보드를 삭제합니다."),
        request_body=BoardDestroySerializer,
        responses={204: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("보드"), ]
    )
    def delete(self, request):
        serializer = BoardDestroySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            Board.objects.filter(
                user=request.user,
                id__in=serializer.validated_data["boards"]
            ).delete()

        return Response(status=HTTP_204_NO_CONTENT, data=MessageSerializer({"message": _("보드를 삭제했습니다.")}).data)


my_board_view = MyBoardView.as_view()


class ScrapBoardView(BaseAPIView):
    allowed_method = ("GET", "POST")

    @swagger_auto_schema(
        operation_id=_("Get Scrap Board"),
        operation_description=_("저장 페이지에 보여질 보드들 입니다."),
        responses={200: openapi.Response(_("OK"), ScrapBoardSerializer)},
        tags=[_("보드"), ],
    )
    def get(self, request):
        scrapped_board = self.request.user.scrap.all()
        data = ScrapBoardSerializer(scrapped_board, many=True).data

        return Response(status=HTTP_200_OK, data=data)


scrap_board_view = ScrapBoardView.as_view()
