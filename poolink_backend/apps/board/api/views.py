from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from poolink_backend.apps.board.api.serializers import (
    BoardSerializer,
    MyBoardSerializer,
    ScrapBoardSerializer,
)
from poolink_backend.apps.board.models import Board
from poolink_backend.apps.category.api.serializers import CategorySerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    # filterset_fields = ["name"]

    @action(detail=True, methods=['get'])
    def categories(self, request, pk):
        board = get_object_or_404(Board, pk=pk)
        categories = board.category.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class MyBoardView(BaseAPIView):
    allowed_method = ("GET", "POST")

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


my_board_view = MyBoardView.as_view()


class ScrapBoardView(BaseAPIView):
    allowed_method = ("GET", "POST")

    @swagger_auto_schema(
        operation_id=_("Get My Board"),
        operation_description=_("저장 페이지에 보여질 보드들 입니다."),
        responses={200: openapi.Response(_("OK"), ScrapBoardSerializer)},
        tags=[_("보드"), ],
    )
    def get(self, request):
        scrapped_board = self.request.user.scrap.all()
        data = ScrapBoardSerializer(scrapped_board, many=True).data

        return Response(status=HTTP_200_OK, data=data)


scrap_board_view = ScrapBoardView.as_view()
