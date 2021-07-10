from rest_framework import serializers

from poolink_backend.apps.category.models import Category
from poolink_backend.bases.api.serializers import ModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'color']


class CategorySelectSerializer(serializers.Serializer):
    category = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=Category.objects.latest('id').id),
        write_only=True,
    )
