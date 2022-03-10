from django.db.models.functions import Length
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
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
