from django.urls import path

from .api.views import link_search_view, link_view

app_name = "links"
urlpatterns = [
    path("", view=link_view),
    path("search", link_search_view),
]
