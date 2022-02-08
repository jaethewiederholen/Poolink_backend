from django.urls import path

from .api.views import scrap_board_view

app_name = "boards"
urlpatterns = [
    path("scrap", view=scrap_board_view),
]
