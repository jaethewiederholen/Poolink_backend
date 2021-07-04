from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from poolink_backend.apps.users.models import User


class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = User
        fields = ("username", "name", "email")


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ("username", "name", "email")
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
            "email": {"unique": _("This email has already been taken.")},
        }
