from rest_framework import serializers

from poolink_backend.apps.category.models import Category
from poolink_backend.bases.api.serializers import ModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'color']


class CategorySelectSerializer(serializers.Serializer):
    try:
        latest = Category.objects.latest('id').id
    except Category.DoesNotExist:
        latest = 0
    category = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=latest),
        write_only=True,
    )
