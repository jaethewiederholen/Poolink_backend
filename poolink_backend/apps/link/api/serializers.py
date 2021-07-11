from rest_framework import serializers

from poolink_backend.apps.link.models import Link
from poolink_backend.bases.api.serializers import ModelSerializer


class LinkSerializer(ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'


class LinkDestroySerializer(serializers.Serializer):
    try:
        latest = Link.objects.latest('id').id
    except Link.DoesNotExist:
        latest = 0
    links = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=latest),
        write_only=True,
    )


class LinkSearchSerializer(serializers.Serializer):
    text = serializers.CharField(
        max_length=None,
        min_length=None,
        allow_blank=True,
        trim_whitespace=True
    )
