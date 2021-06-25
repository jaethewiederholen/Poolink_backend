from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from poolink_backend.apps.board.api.views import BoardViewSet
from poolink_backend.apps.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# base 의 viewset 으로 만들어진 view 들
router.register("users", UserViewSet)
router.register("board", BoardViewSet)


app_name = "api"
urlpatterns = [
    # 기존 viewset 으로 만들어진 것이 아닌 view 들
] + router.urls
