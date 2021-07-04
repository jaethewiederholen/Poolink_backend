from poolink_backend.apps.link.api.serializers import LinkSerializer
from poolink_backend.apps.link.models import Link
from poolink_backend.bases.api.viewsets import ModelViewSet

from rest_framework import decorators


class BoardViewSet(ModelViewSet):
    serializer_class = LinkSerializer
    queryset = Link.objects.all()
    filterset_fields = ["label", "url"]

