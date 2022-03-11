from datetime import datetime, timezone
from json.decoder import JSONDecodeError

import requests
from allauth.socialaccount.providers.google import views as google_view
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import OutstandingToken, RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from config.settings import base as settings
from poolink_backend.apps.notification.api.serializers import UserNotificationSerializer
from poolink_backend.apps.notification.models import Notification
from poolink_backend.apps.users.api.serializers import (
    CustomTokenRefreshSerializer,
    DuplicateCheckSerializer,
    LogoutSerializer,
    SignupSerializer,
    ValidateRefreshTokenSerializer,
)
from poolink_backend.apps.users.models import Path, User
from poolink_backend.bases.api.paginations import SmallResultsSetPagination
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView

from .serializers import (
    GoogleLoginSerializer,
    UserLoginSuccessSerializer,
    UserSerializer,
)

state = settings.STATE
BASE_URL = settings.GOOGLE_BASE_URL
GOOGLE_CALLBACK_URI = BASE_URL + 'google/callback/'


def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id="
                    f"{client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    client_secret = settings.SOCIAL_AUTH_GOOGLE_SECRET
    code = request.GET.get('code')
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret="
        f"{client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    return JsonResponse({"access_token": access_token}, json_dumps_params={'ensure_ascii': False})


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_id="users-login-google",
    operation_description=_(""),
    request_body=GoogleLoginSerializer,
    responses={
        HTTP_200_OK: UserLoginSuccessSerializer,
    }))
class GoogleLogin(SocialLoginView):

    def check_email(self):
        access_token = self.request.data['access_token']
        profile_request = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        print("***************************************check profile*************************************")
        profile_json = profile_request.json()
        email = profile_json.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            return True
        else:
            return False

    def exception(self):
        is_email_user = self.check_email()
        if not is_email_user:
            return JsonResponse({"err_msg": "email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post

    def get_response(self):
        self.exception()
        email = self.user.socialaccount_set.values("extra_data")[0].get("extra_data")['email']
        # username = self.user.socialaccount_set.values("extra_data")[0].get("extra_data")['email'].split('@')[0]
        user = User.objects.get_or_create(email=email)[0]
        response = super().get_response()

        prefer = []
        for i in range(len(user.prefer.through.objects.filter(user=user))):
            prefer.append(user.prefer.through.objects.filter(user=user)[i].category.id)

        # 이전 refresh 토큰 폐기
        # if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
        #     user_refresh = OutstandingToken.objects.filter(user=user)
        #     if user_refresh.count() > 1:
        #         last_refresh = user_refresh.order_by('-created_at')[1].token
        #         blacklist_refresh = RefreshToken(last_refresh)
        #         try:
        #             blacklist_refresh.blacklist()
        #         except AttributeError:
        #             pass

        result = {}
        result["user_id"] = user.id
        result["username"] = user.username
        result["name"] = user.name
        result["email"] = user.email
        result["prefer"] = prefer
        result["access_token"] = response.data["access_token"]
        result["refresh_token"] = response.data["refresh_token"]

        res = Response(status=HTTP_200_OK, data=result)
        # res['Access-Control-Allow-Origin'] = '*'
        # res.set_cookie('access_token', response.data["access_token"], httponly=True,
        #                domain=".poolink.io")
        # res['access-control-expose-headers'] = 'Set-Cookie'
        return res

    adapter_class = google_view.GoogleOAuth2Adapter


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class ValidateRefreshTokenView(BaseAPIView):
    allowed_method = "POST"
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_id=_("Validate Refresh Token"),
        operation_description=_("유효하다면 현재 access 반환 / 유효하지 않다면 오류반환"),
        request_body=ValidateRefreshTokenSerializer,
        responses={200: openapi.Response(_("OK"), ValidateRefreshTokenSerializer)},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        now = datetime.now(timezone.utc)

        try:
            expires_at = OutstandingToken.objects.get(token=refresh_token).expires_at

            # 유효하면 (만료되지 않은 토큰)
            if not RefreshToken(refresh_token).check_blacklist() and now < expires_at:
                return Response(status=HTTP_200_OK,
                                data=MessageSerializer({"message": _("valid refresh token")}).data)

        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=MessageSerializer({"message": _("invalid refresh token")}).data)


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # 특정 유저 알림 api users/{user:id}/notification
    @action(detail=True, url_path='notification')
    @swagger_auto_schema(
        operation_id=_("유저 알림"),
        operation_description=_("특정 유저의 알림 내역을 반환합니다."),
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
    )
    def notification(self, request, pk=None):
        paginator = SmallResultsSetPagination()
        try:
            user_obj = self.get_object()
            if user_obj:
                result = Notification.objects.filter(receiver=user_obj)
                page = paginator.paginate_queryset(result, request)
                serializer = UserNotificationSerializer(page, many=True, context={'request': request})
                return paginator.get_paginated_response(serializer.data)
        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND,
                            data=MessageSerializer({"message": _("존재하지 않는 유저입니다.")}).data)


class UserSignupView(BaseAPIView):
    allowed_method = "PUT"

    @swagger_auto_schema(
        operation_id=_("Sign Up"),
        operation_description=_("유저 회원가입 - 추가정보"),
        request_body=SignupSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("회원가입"), ],
    )
    def put(self, request):
        user = request.user
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data["username"]
            name = serializer.validated_data["name"]
            path = serializer.validated_data["path"]
            is_agreed_to_terms = serializer.validated_data["is_agreed_to_terms"]
            user.update(username=username, name=name, is_agreed_to_terms=is_agreed_to_terms)
            Path.objects.create(path=path)
        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("회원가입 완료")}).data)


class UserLogoutView(BaseAPIView):
    allowed_method = "POST"
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_id=_("Logout User"),
        operation_description=_("유저 로그아웃"),
        request_body=LogoutSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("로그아웃, 탈퇴"), ],
    )
    def post(self, request):
        try:
            logout(request)
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT,
                            data=MessageSerializer({"message": _("로그아웃이 완료되었습니다.")}).data)

        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request):
    #     logout(request)
    #     # reset = ''
    #     res = Response(data=MessageSerializer({"message": _("로그아웃이 완료되었습니다.")}).data)
    #     # res.set_cookie('access_token', reset)
    #     # res.delete_cookie('access_token')
    #     return res


class UserDeleteView(BaseAPIView):
    allowed_method = "DELETE"

    @swagger_auto_schema(
        operation_id=_("Delete User"),
        operation_description=_("회원 탈퇴 - 현재 요청을 보내는 유저를 삭제합니다."),
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("로그아웃, 탈퇴"), ],
    )
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("유저를 삭제했습니다.")}).data)


class DuplicateCheckView(BaseAPIView):
    allowed_method = "POST"

    @swagger_auto_schema(
        operation_id=_("Check duplicate username"),
        operation_description=_("유저네임 중복 확인 합니다."),
        request_body=DuplicateCheckSerializer,
        responses={200: openapi.Response(_("OK"), MessageSerializer),
                   409: openapi.Response(_("CONFLICT"), MessageSerializer)},
        tags=[_("회원가입")],
    )
    def post(self, request):
        serializer = DuplicateCheckSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data["username"]
            try:
                _username = User.objects.get(username=username)
            except (Exception,):
                _username = None

            if not _username:
                return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("사용가능한 유저네임입니다.")}).data)
            else:
                return Response(status=HTTP_409_CONFLICT,
                                data=MessageSerializer({"message": _("이미 사용중인 유저네임입니다.")}).data)


duplicate_check_view = DuplicateCheckView.as_view()
user_signup_view = UserSignupView.as_view()
user_logout_view = UserLogoutView.as_view()
user_delete_view = UserDeleteView.as_view()
