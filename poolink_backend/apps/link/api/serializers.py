from poolink_backend.apps.link.models import Link
from poolink_backend.bases.api.serializers import ModelSerializer


class LinkSerializer(ModelSerializer):
    class Meta:
        model = Link
        fields = (
            "favicon",
            "board",
            "label",
            "url",
        )


class DetailLinkSerializer(ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'
