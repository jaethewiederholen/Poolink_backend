from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend as DrfFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, viewsets
from url_filter.integrations.drf import DjangoFilterBackend as UrlFilter


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_id="리스트조회",
        operation_description="리스트 반환하는 API입니다",
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_id="객체조회",
        operation_description="객체 1개 반환하는 API입니다",
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_id="생성",
        operation_description="객체 1개 생성하는 API입니다",
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_id="부분수정",
        operation_description="객체 1개 부분 수정하는 API입니다",
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_id="전체수정",
        operation_description="객체 1개 전체 수정하는 API입니다",
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_id="삭제",
        operation_description="객체 1개 삭제하는 API입니다",
    ),
)
class ModelViewSet(viewsets.ModelViewSet):
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DrfFilter,
        UrlFilter,
    ]
    ordering_fields = "__all__"
