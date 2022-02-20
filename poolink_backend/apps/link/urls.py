from django.urls import path

from .api.views import link_search_view

app_name = "links"
urlpatterns = [
    path("search", link_search_view),
]
