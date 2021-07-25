from django.urls import path

from .api.views import (
    duplicate_check_view,
    google_login_view,
    user_delete_view,
    user_logout_view,
)

app_name = "users"
urlpatterns = [
    path("", view=user_delete_view),
    path("/logout", view=user_logout_view),
    path("/googlelogin", google_login_view),
    path("/check-duplicate", view=duplicate_check_view),
]
