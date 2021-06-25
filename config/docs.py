from django.urls import include, path

from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_url_patterns = [
    path(r"^api/v1/", include("config.api_router")),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Poolink API Document",
        default_version="v1",
        description="Poolink API Document",
        # terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="herakjy0705@naver.com"),
        license=openapi.License(name="Copyright JaeYeon Kim, Yewon Choi"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=schema_url_patterns,
)
