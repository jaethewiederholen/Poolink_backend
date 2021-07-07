from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView as BaseAPIView

from poolink_backend.apps.category.api.serializers import CategorySerializer
from poolink_backend.apps.category.models import Category
from poolink_backend.bases.api.viewsets import ModelViewSet

from rest_framework import decorators


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

