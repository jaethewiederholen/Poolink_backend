import math

from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from poolink_backend.apps.board.api.serializers import (
    BoardCreateSerializer,
    BoardDestroySerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    MyBoardSerializer,
    PartialBoardSerializer,
    ScrapBoardDestroySerializer,
    ScrapBoardSerializer,
)
from poolink_backend.apps.board.models import Board
from poolink_backend.apps.category.models import Category
from poolink_backend.apps.pagination import CustomPagination
from poolink_backend.apps.permissions import IsWriterOrReadonly
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    permission_classes = ([IsWriterOrReadonly])
    serializer_class = BoardSerializer
    queryset = Board.objects.all()

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request)
        board_id = kwargs['pk']
        board = Board.objects.get(id=board_id)
        return Response(status=HTTP_200_OK, data=BoardUpdateSerializer(board).data)

    def retrieve(self, request, *args, **kwargs):
        board = Board.objects.get(id=kwargs['pk'])
        return Response(status=HTTP_200_OK, data=BoardUpdateSerializer(board).data)
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
        operation_description=_("??????????????? ????????? ????????? ?????????."),
        responses={200: openapi.Response(_("OK"), PartialBoardSerializer, )},
        tags=[_("??? ??????"), ],
    )
    def partial(self, request):
        paginator = CustomPagination()
        user = self.request.user
        boards = Board.objects.filter(user_id=user.id)
        result = paginator.paginate_queryset(boards, request)
        data_count = len(boards)
        page_count = math.ceil(data_count / 30)

        return Response(status=HTTP_200_OK, data={"dataCount": data_count,
                                                  "totalPageCount": page_count,
                                                  "results": PartialBoardSerializer(result, many=True).data})


class MyBoardView(BaseAPIView):
    allowed_method = ("GET", "POST", "DELETE")

    @swagger_auto_schema(
        operation_id=_("Get My Board"),
        operation_description=_("?????? ???????????? ????????? ????????? ?????????."),
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='integer')],
        responses={200: openapi.Response(_("OK"), MyBoardSerializer, )},
        tags=[_("??? ??????"), ],
    )
    def get(self, request):
        paginator = CustomPagination()
        user = self.request.user
        my_board = Board.objects.filter(user_id=user.id)
        scrapped_board = self.request.user.scrap.all()

        boards = my_board.union(scrapped_board)
        result = paginator.paginate_queryset(boards, request)

        data_count = len(boards)
        page_count = math.ceil(data_count / 30)

        return Response(status=HTTP_200_OK, data={"dataCount": data_count,
                                                  "totalPageCount": page_count,
                                                  "results": MyBoardSerializer(result, many=True).data})

    @swagger_auto_schema(
        operation_id=_("Create My Board"),
        operation_description=_("????????? ???????????????."),
        request_body=BoardCreateSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("??? ??????"), ],
    )
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = BoardCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_board = serializer.save()
            new_board.update(image=Category.objects.get(id=serializer.validated_data["category"][0]).image)
            data = {"id": new_board.id}
            data.update(MessageSerializer({"message": _("????????? ??????????????????.")}).data)
            return Response(
                status=HTTP_200_OK,
                data=data,
            )

    @swagger_auto_schema(
        operation_id=_("Delete My Board"),
        operation_description=_("????????? ???????????????."),
        request_body=BoardDestroySerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer),
                   400: openapi.Response(_("Bad Request"), MessageSerializer)},
        tags=[_("??? ??????"), ]
    )
    def delete(self, request):
        serializer = BoardDestroySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            query = Board.objects.filter(
                user=request.user,
                id__in=serializer.validated_data["boards"]
            )
            if not query:
                return Response(status=HTTP_400_BAD_REQUEST,
                                data=MessageSerializer({"message": _("???????????? ????????? ????????? ???????????? ?????? ???????????????.")}).data)
            else:
                query.delete()
                return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("????????? ??????????????????.")}).data)


my_board_view = MyBoardView.as_view()


class ScrapBoardView(BaseAPIView):
    allowed_method = ("GET", "DELETE", "POST")

    @swagger_auto_schema(
        operation_id=_("Scrap Board"),
        operation_description=_("????????? ????????? ?????????."),
        request_body=ScrapBoardSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("????????? ??????"), ],
    )
    def post(self, request):
        user = request.user
        serializer = ScrapBoardSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            board_to_scrap = Board.objects.get(id=serializer.validated_data["board_to_scrap"])
            user.scrap.add(board_to_scrap)
            data = MessageSerializer({"message": _("????????? ?????????????????????.")}).data
            return Response(
                status=HTTP_200_OK,
                data=data,
            )

    @swagger_auto_schema(
        operation_id=_("Delete Scrap Board"),
        operation_description=_("????????? ????????? ???????????????."),
        request_body=ScrapBoardDestroySerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("????????? ??????"), ]
    )
    def delete(self, request):
        serializer = ScrapBoardDestroySerializer(data=request.data)
        user = request.user
        if serializer.is_valid(raise_exception=True):
            query = user.scrap.through.objects.filter(
                board__in=serializer.validated_data["scrap_boards"]
            )
            if not query:
                return Response(status=HTTP_400_BAD_REQUEST,
                                data=MessageSerializer({"message": _("????????? ?????? ????????? ????????? ???????????? ?????? ????????????????????????.")}).data)
            else:
                query.delete()
                return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("???????????? ??????????????????.")}).data)


scrap_board_view = ScrapBoardView.as_view()
