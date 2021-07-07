from poolink_backend.apps.category.models import Category
from poolink_backend.apps.board.api.serializers import (
    BoardSerializer
)
from poolink_backend.bases.api.serializers import ModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'image', 'color']
