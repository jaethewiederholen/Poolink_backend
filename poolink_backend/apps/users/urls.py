from django.urls import path

from .api.views import google_login_view, user_delete_view, user_logout_view, user_signup_view

app_name = "users"
urlpatterns = [
    path("", view=user_delete_view),
    path("/signup", view=user_signup_view),
    path("/logout", view=user_logout_view),
    path("/googlelogin", google_login_view),
]
