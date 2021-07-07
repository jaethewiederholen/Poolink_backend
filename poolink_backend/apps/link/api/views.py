# from django.utils.translation import ugettext_lazy as _
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.response import Response
# from rest_framework.status import HTTP_200_OK

from poolink_backend.apps.link.api.serializers import LinkSerializer
# from poolink_backend.bases.api.views import APIView as BaseAPIView
from poolink_backend.apps.link.models import Link
from poolink_backend.bases.api.viewsets import ModelViewSet


class LinkViewSet(ModelViewSet):
    serializer_class = LinkSerializer
    queryset = Link.objects.all()
