from poolink_backend.apps.board.models import Board
from poolink_backend.bases.api.serializers import ModelSerializer


class BoardSerializer(ModelSerializer):
    class Meta:
        model = Board
        fields = ['name', 'bio', 'image', 'user']
