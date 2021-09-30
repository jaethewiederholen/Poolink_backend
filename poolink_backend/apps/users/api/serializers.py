from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from poolink_backend.apps.users.models import Path
from poolink_backend.bases.api.serializers import ModelSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["user_id", "username", "name", "email", "prefer", "is_agreed_to_terms", ]

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
    # token = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user_id",
            "username",
            "name",
            "email",
            "prefer",
            "is_agreed_to_terms",
        )

    # def get_token(self, obj):
    #     return obj.access_token

    def get_user_id(self, instance):
        return instance.id

    # def get_refresh_token(self, instance):
    #     refresh_token =
    #     return refresh_token


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
    is_agreed_to_terms = serializers.BooleanField()


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.ReadOnlyField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])

        data = {'access_token': str(refresh.access_token)}
        return data


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
