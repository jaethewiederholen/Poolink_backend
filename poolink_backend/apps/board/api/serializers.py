from rest_framework import serializers

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.link.api.serializers import LinkSerializer
from poolink_backend.bases.api.serializers import ModelSerializer


class BoardSerializer(ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'image', 'user', 'links', 'category', 'scrap']


class PartialBoardSerializer(ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'image']


class MyBoardSerializer(ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'image', 'user', 'links', 'category', 'scrap']


class ScrapBoardSerializer(serializers.Serializer):
    board_to_scrap = serializers.IntegerField(
        min_value=0, max_value=Board.objects.latest('id').id, write_only=True,
    )


class BoardDestroySerializer(serializers.Serializer):
    boards = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=Board.objects.latest('id').id),
        write_only=True,
    )


class ScrapBoardDestroySerializer(serializers.Serializer):
    scrap_boards = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=Board.scrap.through.objects.latest('id').id),
        write_only=True,
    )
