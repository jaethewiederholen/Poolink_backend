from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from poolink_backend.apps.board.api.serializers import (
    BoardCreateSerializer,
    BoardDestroySerializer,
    BoardSerializer,
    MyBoardSerializer,
    PartialBoardSerializer,
    ScrapBoardDestroySerializer,
    ScrapBoardSerializer,
)
from poolink_backend.apps.board.models import Board
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()

    # @action(detail=True, methods=['get', 'post'])
    # def categories(self, request, pk):
    #     if request.method == 'GET':
    #         board = get_object_or_404(Board, pk=pk)
    #         categories = board.category.all()
    #         serializer = CategorySerializer(categories, many=True)
    #         return Response(serializer.data)
    #
    #     if request.method == 'POST':
    #         board = get_object_or_404(Board, pk=pk)
    #         before_category_id = []
    #         for i in range(len(board.category.through.objects.all())):
    #             before_category_id.append(board.category.through.objects.all()[i].category.id)
    #         after_category_id = request.data["category"]
    #
    #         delete_category = list(set(before_category_id) - set(after_category_id))
    #         add_category = list(set(after_category_id) - set(before_category_id))
    #
    #         for i in range(0, len(before_category_id)):
    #             for j in range(0, len(delete_category)):
    #                 if before_category_id[i] == delete_category[j]:
    #                     board.category.through.objects.get(category_id=delete_category[i]).delete()
    #
    #         for i in add_category:
    #             board.category.add(i)
    #
    #         result = serializers.Serializer("json", board.category.through.objects.all())
    #         return HttpResponse(result)

    @action(detail=False)
    @swagger_auto_schema(
        operation_id=_("Get My Board Partial Info"),
        operation_description=_("사이드바에 보여질 보드들 입니다."),
        responses={200: openapi.Response(_("OK"), PartialBoardSerializer, )},
        tags=[_("내 보드"), ],
    )
    def partial(self, request):
        user = self.request.user
        board = Board.objects.filter(user_id=user.id)
        serializer = PartialBoardSerializer(board, many=True)
        return Response(serializer.data)


class MyBoardView(BaseAPIView):
    allowed_method = ("GET", "POST", "DELETE")

    @swagger_auto_schema(
        operation_id=_("Get My Board"),
        operation_description=_("저장 페이지에 보여질 보드들 입니다."),
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='integer')],
        responses={200: openapi.Response(_("OK"), MyBoardSerializer,)},
        tags=[_("내 보드"), ],
    )
    def get(self, request):
        paginator = PageNumberPagination()
        user = self.request.user
        my_board = Board.objects.filter(user_id=user.id)
        scrapped_board = self.request.user.scrap.all()
        boards = my_board | scrapped_board
        result = paginator.paginate_queryset(boards, request)

        return Response(status=HTTP_200_OK, data=MyBoardSerializer(result, many=True).data)

    @swagger_auto_schema(
        operation_id=_("Create My Board"),
        operation_description=_("보드를 추가합니다."),
        request_body=BoardCreateSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("내 보드"), ],
    )
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = BoardCreateSerializer(data=request.data)
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
        tags=[_("내 보드"), ]
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
    allowed_method = ("GET", "DELETE", "POST")

    @swagger_auto_schema(
        operation_id=_("Scrap Board"),
        operation_description=_("보드를 스크랩 합니다."),
        request_body=ScrapBoardSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("스크랩 보드"), ],
    )
    def post(self, request):
        user = request.user
        serializer = ScrapBoardSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            board_to_scrap = Board.objects.get(id=serializer.validated_data["board_to_scrap"])
            user.scrap.add(board_to_scrap)
            data = MessageSerializer({"message": _("보드를 스크랩했습니다.")}).data
            return Response(
                status=HTTP_200_OK,
                data=data,
            )

    @swagger_auto_schema(
        operation_id=_("Delete Scrap Board"),
        operation_description=_("스크랩 보드를 삭제합니다."),
        request_body=ScrapBoardDestroySerializer,
        responses={204: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("스크랩 보드"), ]
    )
    def delete(self, request):
        serializer = ScrapBoardDestroySerializer(data=request.data)
        user = request.user
        if serializer.is_valid(raise_exception=True):
            user.scrap.through.objects.filter(
                board__in=serializer.validated_data["scrap_boards"]
            ).delete()

        return Response(status=HTTP_204_NO_CONTENT, data=MessageSerializer({"message": _("스크랩 보드를 삭제했습니다.")}).data)


scrap_board_view = ScrapBoardView.as_view()
