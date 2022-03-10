from rest_framework import serializers

from poolink_backend.apps.hashtag.models import Hashtag
from poolink_backend.bases.api.serializers import ModelSerializer


class HashtagSerializer(ModelSerializer):
    tag_id = serializers.SerializerMethodField()

    class Meta:
        model = Hashtag
        fields = ['tag_id', 'name']

    def get_tag_id(self, instance):
        return instance.id


class HahtagSelectSerialilzer(serializers.Serializer):
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )
