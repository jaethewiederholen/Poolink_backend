import math

from rest_framework.response import Response
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'dataCount': self.page.paginator.count,
            'totalPageCount': math.ceil(self.page.paginator.count / 30),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
