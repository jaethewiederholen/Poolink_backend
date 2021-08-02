from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from poolink_backend.apps.link.api.serializers import (
    LinkDestroySerializer,
    LinkSearchSerializer,
    LinkSerializer,
)
from poolink_backend.apps.link.grabicon import Favicon
from poolink_backend.apps.link.models import Board, Link
from poolink_backend.apps.link.opengraph import LinkImage
from poolink_backend.apps.pagination import CustomPagination
from poolink_backend.apps.permissions import IsWriterOrReadonly, LinkDeletePermission
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class LinkViewSet(ModelViewSet):
    permission_classes = ([IsWriterOrReadonly])
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
        paginator = CustomPagination()
        paginator.page_size = 50
        page_count = paginator.get_page_number(request, paginator=paginator)
        user = self.request.user
        filtered_board = Board.objects.filter(category__in=user.prefer.through.objects.values('category_id'))
        links = Link.objects.filter(board__in=filtered_board, show=True)
        result = paginator.paginate_queryset(links, request)
        data_count = len(result)

        return Response(status=HTTP_200_OK, data={"dataCount": data_count,
                                                  "totalPageCount": page_count,
                                                  "results": LinkSerializer(result, many=True).data})

    @swagger_auto_schema(
        operation_id=_("Create Link"),
        operation_description=_("링크를 추가합니다."),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                        'board': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                description="링크가 속한 보드 아이디를 입력하세요"),
                                        'label': openapi.Schema(type=openapi.TYPE_STRING,
                                                                description="링크 라벨입니다"),
                                        'url': openapi.Schema(type=openapi.TYPE_STRING,
                                                              description="링크 url을 저장하세요"),
                                        'show': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                               description="링크의 공개 여부를 나타냅니 ")
                                    }),
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("링크"), ],
    )
    @permission_classes([IsWriterOrReadonly])
    def post(self, request):
        if request.user == Board.objects.get(id=request.data['board']).user:
            serializer = LinkSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                favicon = Favicon().get_favicon(serializer.validated_data['url'])
                meta_image = LinkImage().get_link_image(serializer.validated_data['url'])

                Link.objects.create(
                    board=serializer.validated_data['board'],
                    label=serializer.validated_data['label'],
                    url=serializer.validated_data['url'],
                    show=serializer.validated_data['show'],
                    favicon=favicon,
                    meta_image=meta_image
                )
                return Response(
                    status=HTTP_200_OK,
                    data=MessageSerializer({"message": _("링크를 저장했습니다.")}).data,
                )
        else:
            print("유저 다름")
            return Response(data=MessageSerializer({"message": _("접근 권한이 없습니다.")}).data)

    @swagger_auto_schema(
        operation_id=_("Delete My Link"),
        operation_description=_("링크를 삭제합니다."),
        request_body=LinkDestroySerializer,
        responses={204: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("링크"), ]
    )
    @permission_classes([LinkDeletePermission])
    def delete(self, request):
        serializer = LinkDestroySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            query = Link.objects.filter(
                board_id__in=Board.objects.filter(user=request.user).values('id'),
                id__in=serializer.validated_data["links"],
            )
            if not query:
                return Response(status=HTTP_400_BAD_REQUEST,
                                data=MessageSerializer({"message": _("링크 삭제의 권한이 없거나 존재하지 않는 링크입니다.")}).data)
            else:
                query.delete()
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
