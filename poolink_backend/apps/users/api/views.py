from json.decoder import JSONDecodeError

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
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

from config.settings import base as settings
from poolink_backend.apps.users.api.serializers import (
    DuplicateCheckSerializer,
    GoogleLoginSerializer,
    SignupSerializer,
    UserLoginSuccessSerializer,
)
from poolink_backend.apps.users.models import Path, User
from poolink_backend.bases.api.serializers import MessageSerializer
from poolink_backend.bases.api.views import APIView as BaseAPIView

from .serializers import UserSerializer

state = settings.STATE
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'google/callback/'


@swagger_auto_schema(
    method="POST",
    operation_id="users-login-google",
    operation_description=_(""),
    request_body=GoogleLoginSerializer,
    responses={
        HTTP_200_OK: UserLoginSuccessSerializer,
    },
    tags=[_("로그인")],
)
@api_view(("POST",))
@authentication_classes([])
@permission_classes([])
def google_login_view(request):
    serializer = GoogleLoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        access_token = serializer.validated_data["access_token"]
        email_req = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_req_status = email_req.status_code

        if email_req_status != 200:
            return Response({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
        email_req_json = email_req.json()
        email = email_req_json.get('email')

        user, created = User.objects.update_or_create(
            email=email,
        )
        return Response(status=HTTP_200_OK, data=UserLoginSuccessSerializer(user).data)


def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id="
                    f"{client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    client_secret = settings.SOCIAL_AUTH_GOOGLE_SECRET
    code = request.GET.get('code')
    """
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret="
        f"{client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    print("access token: " + access_token)
    """
    Email Request
    """
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


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
        return Response(data=MessageSerializer({"message": _("로그아웃이 완료되었습니다.")}).data)


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
