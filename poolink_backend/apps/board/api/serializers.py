from poolink_backend.apps.board.models import Board
from poolink_backend.apps.link.api.serializers import (
    DetailLinkSerializer,
    LinkSerializer,
)
from poolink_backend.bases.api.serializers import ModelSerializer


class BoardSerializer(ModelSerializer):
    links = DetailLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['name', 'image', 'user', 'links', 'bio', 'scrap', 'category', 'scrap_count', 'links']


class PartialBoardSerializer(ModelSerializer):
    class Meta:
        model = Board
        fields = ['name', 'image']


class MyBoardSerializer(ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['name', 'image', 'user_id', 'links']


class ScrapBoardSerializer(ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['name', 'image', 'user_id', 'links']
