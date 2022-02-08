from django.db.models import Model
from rest_framework import permissions

from poolink_backend.apps.board.models import Board
from poolink_backend.apps.link.models import Link


class IsWriterOrReadonly(permissions.BasePermission):
    # 로그인(인증)한 유저는 데이터 조회, 생성 가능
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # 자신의 정보만 수정, 삭제 가능
        if type(obj) is Link:
            return obj.board.user == request.user or request.user in obj.board.invited_users.all()
        else:
            return obj.user == request.user


class LinkDeletePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # 자신의 정보만 수정, 삭제 가능
        return obj.board.user == request.user


class ProfileUpdatePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # 자신의 정보만 수정, 삭제 가능
        return obj.user == request.user


class BoardPermission(permissions.BasePermission):

    safe_methods = ("HEAD", "OPTIONS", "GET")

    def init(self) -> None:
        super().__init__()

    def has_permission(self, request, view) -> bool:
        if request.method in self.safe_methods:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj: Model) -> bool:
        """Check if request.user is the owener of the object."""
        if request.method in self.safe_methods:
            return True
        if request.method == "DELETE":
            return obj.user == request.user
        else:
            return obj.user == request.user or request.user in obj.invited_users.all()


class LinkPermission(permissions.BasePermission):

    safe_methods = ("HEAD", "OPTIONS", "GET")

    def init(self) -> None:
        super().__init__()

    def has_permission(self, request, view):
        user = request.user
        if request.method == "POST":
            board_id = request.data['board']
            board = Board.objects.get(id=board_id)
            if board.user == user or user in board.invited_users.all():
                return request.user.is_authenticated
            return False
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if type(obj) is Link:
            return obj.board.user == request.user or request.user in obj.board.invited_users.all()
        else:
            return obj.user == request.user
