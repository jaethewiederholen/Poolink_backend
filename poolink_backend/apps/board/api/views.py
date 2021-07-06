from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from poolink_backend.apps.board.api.serializers import (
    BoardSerializer,
    PartialBoardSerializer,
)
from poolink_backend.apps.board.models import Board
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    filterset_fields = ["name"]


class PartialBoardView(BaseAPIView):
    allowed_method = ("GET",)

    @swagger_auto_schema(
        operation_id=_("get partial board info"),
        operation_description=_("좌측 상태 바에 위치할 보드 이름과 이미지 입니다.."),
        responses={200: openapi.Response(_("OK"), PartialBoardSerializer)},
        tags=[_("보드"), ],
    )
    def get(self, request):
        return Response(status=HTTP_200_OK, data=PartialBoardSerializer(request.user.boards).data)


partial_board_view = PartialBoardView.as_view()
