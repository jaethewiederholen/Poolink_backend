from django.urls import path

from .api.views import my_board_view, scrap_board_view

app_name = "boards"
urlpatterns = [
    path("/my", view=my_board_view),
    path("/scrap", view=scrap_board_view),
]
