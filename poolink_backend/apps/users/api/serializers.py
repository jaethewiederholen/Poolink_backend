from django.contrib.auth import get_user_model
from rest_framework import serializers

from poolink_backend.apps.board.api.serializers import PartialBoardSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    boards = PartialBoardSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "name", "email", 'boards']
