from rest_framework import permissions


class IsWriterOrReadonly(permissions.BasePermission):
    # 로그인(인증)한 유저는 데이터 조회, 생성 가능
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # 자신의 정보만 수정, 삭제 가능
        return obj.user == request.user


class ProfileUpdatePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # 자신의 정보만 수정, 삭제 가능
        return obj.user == request.user
