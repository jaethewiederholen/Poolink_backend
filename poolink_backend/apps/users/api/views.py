from json.decoder import JSONDecodeError

import requests
from allauth.socialaccount.providers.google import views as google_view
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenViewBase

from config.settings import base as settings
from poolink_backend.apps.users.api.serializers import (
    DuplicateCheckSerializer,
    SignupSerializer,
    CustomTokenRefreshSerializer, UserLoginSuccessSerializer
)
from poolink_backend.apps.users.models import Path, User
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView

from .serializers import UserSerializer

state = settings.STATE
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'google/callback/'


# @swagger_auto_schema(
#     method="POST",
#     operation_id="users-login-google",
#     operation_description=_(""),
#     request_body=GoogleLoginSerializer,
#     responses={
#         HTTP_200_OK: UserLoginSuccessSerializer,
#     },
#     tags=[_("로그인")],
# )
# @api_view(("POST",))
# @authentication_classes([])
# @permission_classes([])
# def google_login_view(request):
#     serializer = GoogleLoginSerializer(data=request.data)
#     if serializer.is_valid(raise_exception=True):
#         access_token = serializer.validated_data["access_token"]
#         email_req = requests.get(
#             f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
#         email_req_status = email_req.status_code
#
#         if email_req_status != 200:
#             return Response({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
#         email_req_json = email_req.json()
#         email = email_req_json.get('email')
#
#         user, created = User.objects.update_or_create(
#             email=email,
#         )
#         return Response(status=HTTP_200_OK, data=UserLoginSuccessSerializer(user).data)


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


class GoogleLogin(SocialLoginView):
    def check_email(self):
        access_token = self.request.data['access_token']
        profile_request = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
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
        username = self.user.socialaccount_set.values("extra_data")[0].get("extra_data")['email'].split('@')[0]
        user = User.objects.update_or_create(email=email, username=username)[0]
        response = super().get_response()

        prefer = []
        for i in range(len(user.prefer.through.objects.filter(user=user))):
            prefer.append(user.prefer.through.objects.filter(user=user)[i].category.id)

        result = {}
        result["user_id"] = user.id
        result["username"] = user.username
        result["name"] = user.name
        result["email"] = user.email
        result["prefer"] = prefer
        result["refresh_token"] = response.data["refresh_token"]

        res = Response(status=HTTP_200_OK, data=result)
        res.set_cookie('access_token', response.data["access_token"], httponly=True)
        return res

        # result = User.objects.update_or_create(email=email, username=username, )
        #
        # if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
        #     user_refresh = OutstandingToken.objects.filter(user=user)
        #     if user_refresh.count() > 1:
        #         last_refresh = user_refresh.order_by('-created_at')[1].token
        #         blacklist_refresh = RefreshToken(last_refresh)
        #         try:
        #             blacklist_refresh.blacklist()
        #         except AttributeError:
        #             pass
        #
        # refresh_token = response.data["refresh_token"]
        #
        # res = Response(status=HTTP_200_OK, data=
        # [UserLoginSuccessSerializer(result[0]).data,
        #  {"refresh_token": refresh_token}])
        # res.set_cookie('access_token', response.data["access_token"], httponly=True)
        # return res

    adapter_class = google_view.GoogleOAuth2Adapter


class CustomTokenRefreshView(TokenViewBase):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        res = Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("토큰 재발급 완료")}).data)
        res.set_cookie('access_token', serializer.validated_data["access_token"], httponly=True)
        return res


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


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
            user.update(username=username, name=name)
            Path.objects.create(path=path)
        return Response(status=HTTP_200_OK, data=MessageSerializer({"message": _("회원가입 완료")}).data)


class UserLogoutView(BaseAPIView):
    allowed_method = "POST"

    @swagger_auto_schema(
        operation_id=_("Logout User"),
        operation_description=_("유저 로그아웃"),
        responses={200: openapi.Response(_("OK"), MessageSerializer)},
        tags=[_("로그아웃, 탈퇴"), ],
    )
    def post(self, request):
        logout(request)
        reset = ''
        res = Response(data=MessageSerializer({"message": _("로그아웃이 완료되었습니다.")}).data)
        res.set_cookie('access_token', reset)
        return res


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
