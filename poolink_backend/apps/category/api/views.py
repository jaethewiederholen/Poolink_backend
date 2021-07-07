from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView as BaseAPIView

from poolink_backend.apps.category.api.serializers import CategorySerializer
from poolink_backend.apps.category.models import Category
from poolink_backend.apps.users.api.serializers import UserSerializer
from poolink_backend.bases.api.viewsets import ModelViewSet
from rest_framework import decorators, status


class CategoryList(BaseAPIView):
    @swagger_auto_schema(
        operation_id=_("Get Category List"),
        operation_description=_("온보딩 화면에 보일 카테고리 전체 리스트입니다."),
        responses={200: openapi.Response(_("OK"), CategorySerializer, )},
        tags=[_("카테고리"), ],
    )
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


# class CategorySelectView(BaseAPIView):
#     @swagger_auto_schema(
#         operation_id=_("Select Prefer-Category"),
#         operation_description=_("유저가 선호하는 카테고리를 추가/삭제하는 뷰입니다."),
#         responses={200: openapi.Response(_("OK"), CategorySerializer, )},
#         tags=[_("선호 카테고리"), ],
#     )
#     def post(self, request, format=None):
#         user = self.request.user
#         prefer_categories = Category.objects.get(name=request.data['name'])
#         serializer = UserSerializer(prefer_categories, many=True)
#         user.prefer.add(serializer)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
