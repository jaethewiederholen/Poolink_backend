from django_filters.rest_framework import DjangoFilterBackend as DrfFilter
from rest_framework import mixins, viewsets
from rest_framework.views import APIView as _APIView
from url_filter.integrations.drf import DjangoFilterBackend as UrlFilter

from poolink_backend.bases.api.paginations import SmallResultsSetPagination


class APIView(_APIView):
    pass


class GenericViewSet(viewsets.GenericViewSet):

    pagination_class = SmallResultsSetPagination  # 20 items per page
    filter_backends = [DrfFilter, UrlFilter]
    ordering_fields = "__all__"


class ModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """GenericViewSet class with mixins."""
