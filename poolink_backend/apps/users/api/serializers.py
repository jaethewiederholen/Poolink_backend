from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from poolink_backend.apps.users.models import Path
from poolink_backend.bases.api.serializers import ModelSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["user_id", "username", "name", "email", "prefer"]

    def get_user_id(self, instance):
        return instance.id


class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(write_only=True)


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ("key",)
        read_only_fields = ("key",)


class UserLoginSuccessSerializer(UserSerializer):
    token = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user_id",
            "username",
            "name",
            "email",
            "prefer",
            "token",
        )

    def get_token(self, obj):
        return obj.access_token

    def get_user_id(self, instance):
        return instance.id


class DuplicateCheckSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class PathSerializer(ModelSerializer):
    class Meta:
        model = Path
        fields = ["path", ]


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=70,
        min_length=1,
        trim_whitespace=True
    )
    name = serializers.CharField(
        max_length=70,
        min_length=1,
        trim_whitespace=True
    )
    path = serializers.CharField(
        max_length=None,
        min_length=None,
        trim_whitespace=True
    )
