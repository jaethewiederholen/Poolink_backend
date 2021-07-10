from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from poolink_backend.apps.board.api.views import BoardViewSet
from poolink_backend.apps.link.api.views import LinkViewSet
from poolink_backend.apps.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# base 의 viewset 으로 만들어진 view 들
router.register("users", UserViewSet)
router.register("board", BoardViewSet)
router.register("link", LinkViewSet)

app_name = "api"
urlpatterns = [
    # 기존 viewset 으로 만들어진 것이 아닌 view 들s
    path("board", include("poolink_backend.apps.board.urls")),
    path("link", include("poolink_backend.apps.link.urls")),
    path("category/", include("poolink_backend.apps.category.urls")),

] + router.urls
