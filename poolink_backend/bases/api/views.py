from django_filters.rest_framework import DjangoFilterBackend as DrfFilter
from rest_framework import filters, viewsets
from rest_framework.views import APIView as _APIView
from url_filter.integrations.drf import DjangoFilterBackend as UrlFilter

from poolink_backend.bases.api.paginations import StandardResultsSetPagination


class APIView(_APIView):
    pass


class GenericViewset(viewsets.GenericViewSet):

    pagination_classes = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DrfFilter, UrlFilter]
    ordering_fields = "__all__"
