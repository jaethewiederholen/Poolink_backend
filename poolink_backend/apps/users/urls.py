from django.urls import path
from .api.views import (
    duplicate_check_view,
    google_login_view,
    user_signup_view,
    user_delete_view,
    user_logout_view,
    GoogleLogin
)

app_name = "users"
urlpatterns = [
    path("", view=user_delete_view),
    path("signup", view=user_signup_view),
    path("logout", view=user_logout_view),
    # path("/googlelogin", google_login_view),
    path("googlelogin", GoogleLogin.as_view()),
    path("check-duplicate", view=duplicate_check_view),
]
