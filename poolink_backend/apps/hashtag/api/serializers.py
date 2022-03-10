from poolink_backend.apps.hashtag.models import Hashtag
from poolink_backend.bases.api.serializers import ModelSerializer


class HashtagSerializer(ModelSerializer):

    class Meta:
        model = Hashtag
        fields = "__all__"
