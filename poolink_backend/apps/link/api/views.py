from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from poolink_backend.apps.link.api.serializers import (
    LinkDestroySerializer,
    LinkSearchSerializer,
    LinkSerializer,
)
from poolink_backend.apps.link.models import Board, Link
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class LinkViewSet(ModelViewSet):
    serializer_class = LinkSerializer
    queryset = Link.objects.filter(show=True,)


class LinkView(BaseAPIView):
    allowed_method = ["DELETE", "POST", "GET"]
    filterset_fields = ["hide"]

    @swagger_auto_schema(
        operation_id=_("Get Link"),
        operation_description=_("탐색 페이지에서 보여질 링크들입니다. 유저의 선호카테고리로 필터링 됩니다."),
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='integer')],
        responses={200: openapi.Response(_("OK"), LinkSerializer, )},
        tags=[_("링크"), ],
    )
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 50
        user = self.request.user
        filtered_board = Board.objects.filter(category__in=user.prefer.through.objects.values('category_id'))
        links = Link.objects.filter(board__in=filtered_board, show=True)
        result = paginator.paginate_queryset(links, request)

        return Response(status=HTTP_200_OK, data=LinkSerializer(result, many=True).data)

    @swagger_auto_schema(
        operation_id=_("Create Link"),
        operation_description=_("링크를 추가합니다."),
        manual_parameters=[
            openapi.Parameter('hide', openapi.IN_QUERY, type='bool')],
        request_body=LinkSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("링크"), ],
    )
    def post(self, request):
        hide = request.query_params.get('hide', None)
        if hide:
            request.data["show"] = False
        serializer = LinkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                status=HTTP_200_OK,
                data=MessageSerializer({"message": _("링크를 저장했습니다.")}).data,
            )

    @swagger_auto_schema(
        operation_id=_("Delete My Link"),
        operation_description=_("링크를 삭제합니다."),
        request_body=LinkDestroySerializer,
        responses={204: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("링크"), ]
    )
    def delete(self, request):
        serializer = LinkDestroySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            Link.objects.filter(
                board_id__in=Board.objects.filter(user=request.user).values('id'),
                id__in=serializer.validated_data["links"],
            ).delete()

        return Response(status=HTTP_204_NO_CONTENT, data=MessageSerializer({"message": _("링크를 삭제했습니다.")}).data)


link_view = LinkView.as_view()


class LinkSearchView(BaseAPIView):
    allowed_method = ["POST"]
    filterset_fields = ["my"]

    @swagger_auto_schema(
        operation_id=_("Search Link"),
        operation_description=_("링크를 검색합니다."),
        manual_parameters=[
            openapi.Parameter('my', openapi.IN_QUERY, type='bool')],
        request_body=LinkSearchSerializer,
        responses={204: openapi.Response(_("OK"), LinkSearchSerializer)},
        tags=[_("링크"), ]
    )
    def post(self, request):
        user = request.user
        serializer = LinkSearchSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            my = request.query_params.get('my', None)
            # 저장페이지에서 링크 검색
            if my:
                scrapped_board = self.request.user.scrap.all()
                my_board = Board.objects.filter(user_id=user.id)
                boards = scrapped_board | my_board
                links = Link.objects.filter(board__in=boards, label__contains=serializer.validated_data['text'])
            # 탐색페이지에서 링크 검색
            else:
                text = serializer.validated_data['text']
                if "".__eq__(text):
                    filtered_board = Board.objects.filter(
                        category__in=user.prefer.through.objects.values('category_id')
                    )
                    links = Link.objects.filter(board__in=filtered_board, show=True)

                else:
                    links = Link.objects.filter(
                        label__contains=serializer.validated_data['text'],
                        show=True
                    )
        return Response(status=HTTP_200_OK, data=LinkSerializer(links, many=True).data)


link_search_view = LinkSearchView.as_view()
