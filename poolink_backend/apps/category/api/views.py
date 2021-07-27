from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView as BaseAPIView

from poolink_backend.apps.category.api.serializers import (
    CategorySelectSerializer,
    CategorySerializer,
)
from poolink_backend.apps.category.models import Category
from poolink_backend.bases.api.serializers import MessageSerializer


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


class CategorySelectView(BaseAPIView):
    @swagger_auto_schema(
        operation_id=_("Select Prefer-Category"),
        operation_description=_("유저가 선호하는 카테고리를 추가/삭제하는 뷰입니다."),
        request_body=CategorySelectSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer, )},
        tags=[_("선호 카테고리"), ],
    )
    def post(self, request, format=None):
        user = self.request.user
        serializer = CategorySelectSerializer(data=request.data,)
        if serializer.is_valid(raise_exception=True):
            before_category_id = []
            for i in range(len(user.prefer.through.objects.all())):
                before_category_id.append(user.prefer.through.objects.all()[i].category.id)
            after_category_id = serializer.validated_data["category"]

            delete_category = list(set(before_category_id) - set(after_category_id))
            add_category = list(set(after_category_id) - set(before_category_id))

            for i in range(len(before_category_id)):
                for j in range(len(delete_category)):
                    if before_category_id[i] == delete_category[j]:
                        user.prefer.through.objects.get(category_id=delete_category[j]).delete()

            for i in add_category:
                user.prefer.add(i)
            # result = serializers.Serializer("json", user.prefer.through.objects.all())
        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("유저의 선호 카테고리를 설정했습니다.")}).data,)
