from poolink_backend.apps.board.api.serializers import BoardSerializer
from poolink_backend.apps.board.models import Board
from poolink_backend.bases.api.viewsets import ModelViewSet


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    filterset_fields = ["name"]
