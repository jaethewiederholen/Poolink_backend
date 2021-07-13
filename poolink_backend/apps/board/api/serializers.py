from rest_framework import serializers

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.category.api.serializers import CategorySerializer
from poolink_backend.apps.category.models import Category
from poolink_backend.apps.link.api.serializers import LinkSerializer
from poolink_backend.bases.api.serializers import ModelSerializer


class BoardSerializer(ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'user', 'links', 'category', 'scrap']


class BoardCreateSerializer(ModelSerializer):
    try:
        latest = Category.objects.latest('id').id
    except Category.DoesNotExist:
        latest = 0
    category = serializers.ListSerializer(
        child=serializers.IntegerField(
            min_value=0, max_value=latest), write_only=True,)

    class Meta:
        model = Board
        fields = ['name', 'user', 'category']

    def create(self, validated_data):

        category_data = validated_data.pop('category')
        board = Board.objects.create(**validated_data)
        for category in category_data:
            board_category = Category.objects.get(id=category)
            board.category.add(board_category)
        return board


class PartialBoardSerializer(ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'image']


class MyBoardSerializer(ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'image', 'user', 'links', 'category', 'scrap']


class ScrapBoardSerializer(serializers.Serializer):
    try:
        latest = Board.objects.latest('id').id
    except Board.DoesNotExist:
        latest = 0
    board_to_scrap = serializers.IntegerField(
        min_value=0, max_value=latest, write_only=True,
    )


class BoardDestroySerializer(serializers.Serializer):
    try:
        latest = Board.objects.latest('id').id
    except Board.DoesNotExist:
        latest = 0
    boards = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=latest),
        write_only=True,
    )


class ScrapBoardDestroySerializer(serializers.Serializer):
    try:
        latest = Board.scrap.through.objects.latest('id').id
    except Board.scrap.through.DoesNotExist:
        latest = 0
    scrap_boards = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=latest),
        write_only=True,
    )
