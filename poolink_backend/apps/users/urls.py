from django.urls import path

from .api.views import (
    CustomTokenRefreshView,
    GoogleLogin,
    ValidateRefreshTokenView,
    duplicate_check_view,
    user_delete_view,
    user_logout_view,
    user_search_view,
    user_signup_view,
)

app_name = "users"
urlpatterns = [
    path("", view=user_delete_view),
    path("signup", view=user_signup_view),
    path("logout", view=user_logout_view),
    # path("/googlelogin", google_login_view),
    path("googlelogin", GoogleLogin.as_view()),
    path("token/refresh", CustomTokenRefreshView.as_view()),
    path("token/validate", ValidateRefreshTokenView.as_view()),
    path("check-duplicate", view=duplicate_check_view),
    path("search", view=user_search_view),
]
