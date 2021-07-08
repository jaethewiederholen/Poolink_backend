from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from poolink_backend.apps.link.api.serializers import (
    LinkDestroySerializer,
    LinkSerializer,
)
from poolink_backend.apps.link.models import Board, Link
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.bases.api.viewsets import ModelViewSet


class LinkViewSet(ModelViewSet):
    serializer_class = LinkSerializer
    queryset = Link.objects.filter(show=True)


class LinkView(BaseAPIView):
    allowed_method = ["DELETE", "POST"]
    filterset_fields = ["copy"]

    @swagger_auto_schema(
        operation_id=_("Create Link"),
        operation_description=_("링크를 추가합니다."),
        manual_parameters=[
            openapi.Parameter('copy', openapi.IN_QUERY, type='bool')],
        request_body=LinkSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("링크"), ],
    )
    def post(self, request):
        hide = request.query_params.get('copy', None)
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
