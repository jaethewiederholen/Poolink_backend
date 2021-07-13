from django.urls import path

from .api.views import google_login_view

app_name = "users"
urlpatterns = [
    path("/googlelogin", google_login_view),
]
