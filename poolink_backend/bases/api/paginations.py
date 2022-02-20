from rest_framework.pagination import PageNumberPagination


class SmallResultsSetPagination(PageNumberPagination):  # noqa: D101
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class StandardResultsSetPagination(PageNumberPagination):  # noqa: D101
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1000


class LargeResultsSetPagination(PageNumberPagination):  # noqa: D101
    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 10000
