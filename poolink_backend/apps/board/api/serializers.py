import json

from rest_framework import serializers

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.hashtag.api.serializers import HashtagSerializer
from poolink_backend.apps.hashtag.models import Hashtag
from poolink_backend.apps.link.api.serializers import (
    LinkInfoSerializer,
    LinkSerializer,
    PublicLinkSerializer,
)
from poolink_backend.bases.api.serializers import ModelSerializer


# Viewset에 사용되는 serializer
class BoardSerializer(ModelSerializer):
    links = LinkInfoSerializer(many=True, read_only=True)
    board_id = serializers.SerializerMethodField()
    tags = HashtagSerializer(many=True)

    class Meta:
        model = Board
        fields = [
            'board_id',
            'name',
            'user',
            'emoji',
            'bio',
            'links',
            'tags',
            'scrap',
            'invited_users',
            'is_bookmarked',
            'searchable',
            'created',
            'modified'
            ]

    def get_board_id(self, instance):
        return instance.id

    def update(self, instance, validated_data):
        try:
            tag_names = json.loads(json.dumps(validated_data.pop('tags')))
        except KeyError:
            tag_names = None
        if tag_names is not None:
            tags = []
            for t in tag_names:
                obj, created = Hashtag.objects.get_or_create(name=t["name"])
                tags.append(obj)
            instance.tags.set(tags, clear=True)
        return super().update(instance, validated_data)


class SingleBoardSerializer(ModelSerializer):

    links = serializers.SerializerMethodField()
    tags = HashtagSerializer(many=True)
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
            'tags',
            'scrap',
            'invited_users',
            'is_bookmarked',
            'searchable',
            'created',
            'modified'
            ]

    def get_board_id(self, instance):
        return instance.id

    def get_links(self, instance):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user == instance.user or user in instance.invited_users.all():
            return LinkSerializer(instance.links.all(), many=True).data

        else:
            return PublicLinkSerializer(instance.links.all(), many=True).data


class BoardCreateSerializer(ModelSerializer):

    tags = serializers.ListSerializer(
        child=serializers.CharField(max_length=100))

    class Meta:
        model = Board
        fields = ['name', 'user', 'tags']

    def create(self, validated_data):

        tags = validated_data.pop('tags')
        board = Board.objects.create(**validated_data)
        for tag_name in set(tags):
            tag, created = Hashtag.objects.get_or_create(name=tag_name)
            board.tags.add(tag)
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
