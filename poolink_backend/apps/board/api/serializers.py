from rest_framework import serializers

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.category.api.serializers import CategorySerializer
from poolink_backend.apps.category.models import Category
from poolink_backend.apps.link.api.serializers import (
    LinkInfoSerializer,
    LinkSerializer,
    PublicLinkSerializer,
)
from poolink_backend.bases.api.serializers import ModelSerializer


# Viewset에 사용되는 serializer
class BoardSerializer(ModelSerializer):
    links = LinkInfoSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField()
    board_id = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'board_id',
            'name',
            'user',
            'emoji',
            'bio',
            'links',
            'category',
            'scrap',
            'invited_users',
            'is_bookmarked',
            'created',
            'modified'
            ]

    def get_board_id(self, instance):
        return instance.id

    def get_category(self, instance):
        category = instance.category.through.objects.filter(board=instance)
        result = []
        for i in range(len(category)):
            result.append(Category.objects.get(name=category[i].category.name))
        return CategorySerializer(result, many=True).data


class SingleBoardSerializer(ModelSerializer):

    links = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    board_id = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'board_id',
            'name',
            'user',
            'emoji',
            'bio',
            'links',
            'category',
            'scrap',
            'invited_users',
            'is_bookmarked',
            'created',
            'modified'
            ]

    def get_board_id(self, instance):
        return instance.id

    def get_category(self, instance):
        category = instance.category.through.objects.filter(board=instance)
        result = []
        for i in range(len(category)):
            result.append(Category.objects.get(name=category[i].category.name))
        return CategorySerializer(result, many=True).data

    def get_links(self, instance):
        user = None
        request = self.context.get("request")
        print(request)
        if request and hasattr(request, "user"):
            user = request.user
        print(user)
        if user == instance.user or user in instance.invited_users.all():
            return LinkSerializer(instance.links.all(), many=True).data

        else:
            return PublicLinkSerializer(instance.links.all(), many=True).data


class BoardCreateSerializer(ModelSerializer):

    category = serializers.ListSerializer(
        child=serializers.IntegerField())

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


class ScrapBoardSerializer(serializers.Serializer):
    board_to_scrap = serializers.IntegerField(write_only=True)


class BoardDestroySerializer(serializers.Serializer):
    boards = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )


class ScrapBoardDestroySerializer(serializers.Serializer):
    scrap_boards = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )


class BoardInviteSerializer(ModelSerializer):

    class Meta:
        model = Board
        fields = ['invited_users']
