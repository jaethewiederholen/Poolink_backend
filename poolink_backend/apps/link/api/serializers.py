# import requests
from rest_framework import serializers

from poolink_backend.apps.link.models import Link
from poolink_backend.apps.link.opengraph import LinkImage
from poolink_backend.bases.api.serializers import ModelSerializer


class LinkSerializer(ModelSerializer):
    link_id = serializers.SerializerMethodField()
    link_image = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ['link_id', 'board', 'label', 'url', 'show', 'favicon', 'link_image']

    def get_link_id(self, instance):
        return instance.id

    def get_link_image(self, instance):
        # url = requests.get(instance.url).content
        # LinkImage.get_page(url=url)
        # return LinkImage.get_og_iamge(self,soup=soup)
        return LinkImage.get_link_image(self, instance.url)


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
