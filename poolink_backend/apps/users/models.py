from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _


class UserManager(UserManager):
    def create_superuser(self, email, password, **extra_fields):
        return super().create_superuser(email=email, password=password, **extra_fields)

    def create_user(self, email=None, password=None, **extra_fields):
        return super().create_superuser(email=email, password=password, **extra_fields)

    def get_or_create_user(self, name=None, email=None, password=None):
        users = self.model.objects.filter(email=email)
        is_created = False
        if users.exists():
            user = users.first()
            return user, is_created
        is_created = True
        user = self.create_user(name=name, email=email, password=password)
        return user, is_created


class User(
    AbstractUser,
):
    """Default user for Poolink_backend."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    email = models.EmailField(
        "이메일",
        unique=True,
    )

    objects = UserManager()

    class Meta:
        verbose_name = verbose_name_plural = "유저"

    def __str__(self):
        return "{} {}".format(self.name, self.email)
