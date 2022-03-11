from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Length
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView as BaseAPIView

from poolink_backend.apps.hashtag.api.serializers import HashtagSerializer
from poolink_backend.apps.hashtag.models import Hashtag
from poolink_backend.bases.api.serializers import MessageSerializer


class HashtagView(BaseAPIView):

    @swagger_auto_schema(
        operation_id=_("Search Hashtags"),
        operation_description=_("검색어를 포함한 해시태그들을 반환합니다."),
        responses={200: openapi.Response(_("OK"), HashtagSerializer),
                   400: openapi.Response(_("Bad Request"), MessageSerializer)},
        manual_parameters=[
                openapi.Parameter('query', openapi.IN_QUERY, type='string')],
        )
    def get(self, request):
        query = request.query_params.get('query', None)
        if query:
            tags = Hashtag.objects.filter(name__icontains=query).order_by(Length('name').asc())[:10]
            serializer = HashtagSerializer(tags, many=True)
            return Response(status=HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=HTTP_400_BAD_REQUEST,
                            data=MessageSerializer({"message": _("검색어 미입력")}).data)


class PreferredTagView(BaseAPIView):
    @swagger_auto_schema(
        operation_id=_("Add preferred Hashtags"),
        operation_description=_("유저가 선호하는 카테고리를 추가합니다."),
        request_body=HashtagSerializer,
        responses={200: openapi.Response(_("OK"), HashtagSerializer)},
        )
    def post(self, request):
        user = request.user
        serializer = HashtagSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            tag_name = serializer.validated_data["name"]
            tag, created = Hashtag.objects.get_or_create(name=tag_name)
            if not created:
                if tag in user.preferred_tags.all():
                    return Response(status=HTTP_400_BAD_REQUEST,
                                    data=MessageSerializer({"message": _("이미 설정된 선호 태그입니다.")}).data)
            user.preferred_tags.add(tag)
            return Response(status=HTTP_200_OK,
                            data=HashtagSerializer(user.preferred_tags.all(), many=True).data)

    @swagger_auto_schema(
        operation_id=_("Delete preferred Hashtags"),
        operation_description=_("유저가 선호하는 카테고리를 삭제합니다."),
        request_body=HashtagSerializer,
        responses={204: openapi.Response(_("OK"), HashtagSerializer)},
        )
    def delete(self, request):
        user = request.user
        serializer = HashtagSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            tag_name = serializer.validated_data["name"]
            try:
                tag = user.preferred_tags.get(name=tag_name)
            except ObjectDoesNotExist:
                return Response(status=HTTP_400_BAD_REQUEST,
                                data=MessageSerializer({"message": _("존재하지 않는 선호 태그 입니다.")}).data)
            user.preferred_tags.remove(tag)

            return Response(status=HTTP_204_NO_CONTENT,
                            data=HashtagSerializer(user.preferred_tags.all(), many=True).data)
