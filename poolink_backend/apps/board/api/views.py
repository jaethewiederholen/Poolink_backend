from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from poolink_backend.apps.board.api.serializers import (
    BoardSerializer,
    PartialBoardSerializer,
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
    filterset_fields = ["name"]

# 이렇게 뷰셋에서 create 오버라이딩하면 request 해당 유저 보드 생성 가능한가? (출처 https://www.valentinog.com/blog/drf-request/)
#     def create(self, request, *args, **kwargs):
#         request.data['user'] = request.user.id
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get', 'post'])
    def categories(self, request, pk):
        if request.method == 'GET':
            board = get_object_or_404(Board, pk=pk)
            categories = board.category.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            board = get_object_or_404(Board, pk=pk)
            before_category_id = []
            for i in range(len(board.category.through.objects.all())):
                before_category_id.append(board.category.through.objects.all()[i].category.id)
            after_category_id = request.data["category"]

            delete_category = list(set(before_category_id) - set(after_category_id))
            add_category = list(set(after_category_id) - set(before_category_id))

            for i in range(0, len(before_category_id)):
                for j in range(0, len(delete_category)):
                    if before_category_id[i] == delete_category[j]:
                        board.category.through.objects.get(category_id=delete_category[i]).delete()

            for i in add_category:
                board.category.add(i)

            result = serializers.Serializer("json", board.category.through.objects.all())
            return HttpResponse(result)

    @action(detail=False)
    def partial(self, request):
        user = self.request.user
        board = Board.objects.filter(user_id=user.id)
        serializer = PartialBoardSerializer(board, many=True)
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
