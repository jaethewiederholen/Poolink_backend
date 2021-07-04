from poolink_backend.apps.category.api.serializers import CategorySerializer
from poolink_backend.apps.category.models import Category
from poolink_backend.bases.api.viewsets import ModelViewSet

from rest_framework import decorators


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filterset_fields = ["name", "color"]

