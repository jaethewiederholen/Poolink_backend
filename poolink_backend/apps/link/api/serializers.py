from rest_framework import serializers

from poolink_backend.apps.link.models import Link
from poolink_backend.bases.api.serializers import ModelSerializer


class LinkSerializer(ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'


class LinkDestroySerializer(serializers.Serializer):
    links = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=Link.objects.latest('id').id),
        write_only=True,
    )
