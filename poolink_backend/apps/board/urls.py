from django.urls import path

from .api.views import partial_board_view

app_name = "board"
urlpatterns = [
    path("partial", view=partial_board_view),
]
