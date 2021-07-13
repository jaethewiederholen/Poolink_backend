from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from poolink_backend.bases.api.serializers import ModelSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "name", "email", 'boards', 'prefer']


class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(write_only=True)


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ("key",)
        read_only_fields = ("key",)


class UserLoginSuccessSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "email",
            "prefer",
            "token",
        )

    def get_token(self, obj):
        return obj.token.key
