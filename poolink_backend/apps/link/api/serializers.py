from rest_framework import serializers

from poolink_backend.apps.link.models import Link
from poolink_backend.bases.api.serializers import ModelSerializer


class FilteredLinkSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.order_by('-id')[:2]
        return super(FilteredLinkSerializer, self).to_representation(data)


class LinkInfoSerializer(serializers.ModelSerializer):

    class Meta:
        list_serializer_class = FilteredLinkSerializer
        model = Link
        fields = ['board', 'label', 'url', 'favicon', 'meta_image']


class LinkSerializer(ModelSerializer):
    link_id = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ['link_id', 'board', 'label', 'url', 'show', 'favicon', 'meta_image', 'memo']

    def get_link_id(self, instance):
        return instance.id


class LinkDestroySerializer(serializers.Serializer):
    links = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )


class LinkSearchSerializer(serializers.Serializer):
    text = serializers.CharField(
        max_length=None,
        min_length=None,
        allow_blank=True,
        trim_whitespace=True
    )
