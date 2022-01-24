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
    BoardInviteSerializer,
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
from poolink_backend.apps.permissions import BoardPermission
from poolink_backend.apps.users.models import User
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    permission_classes = ([BoardPermission])
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

    # 초대 api boards/{board:id}/invite
    @action(methods=['post'], detail=True, url_path='invite')
    @swagger_auto_schema(
        operation_id=_("Invite Users to Board"),
        operation_description=_("보드에 유저를 초대합니다."),
        request_body=BoardInviteSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
    )
    def invite(self, request, pk):
        invited_users = request.data.get('invited_users')  # 배열
        board = Board.objects.get(id=pk)

        for i in invited_users:
            if User.objects.filter(username=i):  # 유저네임이 존재하면
                board.invited_users.add(User.objects.get(username=i))  # 초대 유저에 추가

        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("유저를 초대했습니다.")}).data)

    @action(detail=False)
    @swagger_auto_schema(
        operation_id=_("Get My Board Partial Info"),
        operation_description=_("사이드바에 보여질 보드들 입니다."),
        responses={200: openapi.Response(_("OK"), PartialBoardSerializer, )},
        tags=[_("내 보드"), ],
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
        operation_description=_("저장 페이지에 보여질 보드들 입니다."),
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='integer')],
        responses={200: openapi.Response(_("OK"), MyBoardSerializer, )},
        tags=[_("내 보드"), ],
    )
    def get(self, request):
        paginator = CustomPagination()
        user = self.request.user
        my_board = Board.objects.filter(user_id=user.id, invited_users__isnull=True)
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
            new_board.update(image=Category.objects.get(id=serializer.validated_data["category"][0]).image)
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
        responses={200: openapi.Response(_("OK"), MessageSerializer),
                   400: openapi.Response(_("Bad Request"), MessageSerializer)},
        tags=[_("내 보드"), ]
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
                                data=MessageSerializer({"message": _("보드삭제 권한이 없거나 존재하지 않는 보드입니다.")}).data)
            else:
                query.delete()
                return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("보드를 삭제했습니다.")}).data)


my_board_view = MyBoardView.as_view()


class SharedBoardView(BaseAPIView):
    allowed_method = ("GET")

    @swagger_auto_schema(
        operation_id=_("Shared Boards"),
        operation_description=_("내가 속한 공유 보드를 조회합니다."),
        responses={200: openapi.Response(_("OK"), MyBoardSerializer,)},
        tags=[_("공유 보드"), ],
    )
    def get(self, request):
        paginator = CustomPagination()
        user = self.request.user

        invited_boards = user.invited_boards.all()
        owned_share_boards = user.boards.filter(invited_users__isnull=False)
        share_boards = owned_share_boards.union(invited_boards)

        result = paginator.paginate_queryset(share_boards, request)

        data_count = len(share_boards)
        page_count = math.ceil(data_count / 30)

        return Response(status=HTTP_200_OK, data={"dataCount": data_count,
                                                  "totalPageCount": page_count,
                                                  "results": MyBoardSerializer(result, many=True).data})


shared_board_view = SharedBoardView.as_view()


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
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("스크랩 보드"), ]
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
                                data=MessageSerializer({"message": _("스크랩 취소 권한이 없거나 존재하지 않는 스크랩보드입니다.")}).data)
            else:
                query.delete()
                return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("스크랩을 취소했습니다.")}).data)


scrap_board_view = ScrapBoardView.as_view()
