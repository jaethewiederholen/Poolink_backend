from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from poolink_backend.apps.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                    "email",
                )
            },
        ),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'name', 'password1', 'password2')}
         ),
    )
    list_filter = ("is_superuser",)
    list_display = [
        "username",
        "name",
        "is_superuser",
    ]
    search_fields = ["username"]


admin.site.register(User, UserAdmin)
