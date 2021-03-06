from rest_framework import permissions

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
            return obj.board.user == request.user
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
