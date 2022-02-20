from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from poolink_backend.apps.board.api.serializers import (
    BoardCreateSerializer,
    BoardDestroySerializer,
    BoardInviteSerializer,
    BoardSerializer,
    ScrapBoardDestroySerializer,
    ScrapBoardSerializer,
    SingleBoardSerializer,
)
from poolink_backend.apps.board.models import Board
from poolink_backend.apps.category.models import Category
from poolink_backend.apps.permissions import BoardPermission
from poolink_backend.apps.users.models import User
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.views import ModelViewSet


class BoardViewSet(ModelViewSet):
    permission_classes = ([BoardPermission])
    serializer_class = BoardSerializer
    queryset = Board.objects.all()

    @swagger_auto_schema(
        operation_id=_("리스트조회"),
        operation_description=_("내보드 또는 공유보드 리스트를 조회합니다."),
        responses={200: openapi.Response(_("OK"), BoardSerializer)},
        manual_parameters=[
            openapi.Parameter('shared', openapi.IN_QUERY, type='boolean')],
    )
    def list(self, request):
        user = request.user
        shared = bool(request.query_params.get('shared', None))
        if shared:
            invited_boards = user.invited_boards.all()
            owned_share_boards = user.boards.filter(invited_users__isnull=False)
            boards = owned_share_boards.union(invited_boards)

        else:
            my_board = Board.objects.filter(user=user, invited_users__isnull=True)
            scrapped_board = self.request.user.scrap.all()
            boards = my_board.union(scrapped_board).order_by('-is_bookmarked')

        return Response(status=HTTP_200_OK, data=BoardSerializer(boards, many=True).data)

    @swagger_auto_schema(
        operation_id=_("생성"),
        operation_description=_("보드를 생성합니다."),
        request_body=BoardCreateSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
    )
    def create(self, request):
        if not request.data['user'] == request.user.id:
            raise PermissionDenied

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
        operation_id=_("객체조회")
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            board = Board.objects.get(id=kwargs['pk'])
        except Board.DoesNotExist:
            raise NotFound
        return Response(status=HTTP_200_OK, data=SingleBoardSerializer(board, context={'request': request}).data)

    @action(methods=['delete'], detail=False, url_path='bulk-delete')
    @swagger_auto_schema(
        operation_id=_("다중삭제"),
        operation_description=_("보드를 삭제합니다."),
        request_body=BoardDestroySerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer),
                   400: openapi.Response(_("Bad Request"), MessageSerializer)},
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

    # 초대 api boards/{board:id}/invite
    @action(methods=['post'], detail=True, url_path='invite')
    @swagger_auto_schema(
        operation_id=_("유저 초대"),
        operation_description=_("보드에 유저를 초대합니다."),
        request_body=BoardInviteSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
    )
    def invite(self, request, pk):
        invited_users = request.data.get('invited_users')  # 배열
        board = Board.objects.get(id=pk)

        for i in invited_users:
            if request.user.username == i:
                return Response(status=HTTP_400_BAD_REQUEST,
                                data=MessageSerializer({"message": _("보드 소유자는 초대 대상이 아닙니다.")}).data)
            elif i in board.invited_users.all().values_list("username", flat=True):
                # 이미 초대된 유저는 다시 초대하지 않고 넘긴다.
                pass
            try:
                board.invited_users.add(User.objects.get(username=i))  # 초대 유저에 추가
            except ObjectDoesNotExist:
                return Response(status=HTTP_404_NOT_FOUND,
                                data=MessageSerializer({"message": _("존재하지 않는 유저입니다.")}).data)
        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("유저를 초대했습니다.")}).data)


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
