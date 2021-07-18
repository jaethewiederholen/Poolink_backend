from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from poolink_backend.bases.api.serializers import ModelSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["user_id", "username", "name", "email", 'boards', 'prefer']

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
        return obj.token.key

    def get_user_id(self, instance):
        return instance.id
