from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from poolink_backend.bases.models import Model
from poolink_backend.apps.category.models import Category


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(
        self, username=None, email=None, password=None, name=None, **extra_fields
    ):
        if not email:
            raise ValueError("must have user email")
        if not password:
            raise ValueError("must have user password")
        user = self.model(
            email=self.normalize_email(email), username=username, name=name

        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, name, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            name=name,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

    def get_or_create_user(self, username=None, name=None, email=None, password=None):
        users = self.model.objects.filter(email=email)
        is_created = False
        if users.exists():
            user = users.first()
            return user, is_created
        is_created = True
        user = self.create_user(
            username=username, name=name, email=email, password=password
        )
        return user, is_created


class User(AbstractBaseUser, Model, PermissionsMixin):
    """Default user for Poolink_backend."""

    username = models.CharField(
        verbose_name=_("유저 이름"),
        help_text=_("유니크한 유저 이름입니다."),
        null=False,
        max_length=70,
        unique=True,
    )
    #: First and last name do not cover name patterns around the globe
    name = models.CharField(
        verbose_name=_("유저 실명"),
        help_text=_("유저의 실명입니다."),
        null=False,
        max_length=70,
    )
    email = models.EmailField(
        verbose_name=_("유저 이메일"),
        help_text=_("유니크한 유저의 이메일입니다."),
        null=False,
        max_length=70,
        unique=True,
    )
    prefer = models.ManyToManyField(
        Category,
        related_name="prefer_category",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    is_superuser = models.BooleanField(
        verbose_name=_("is_superuser"),
        default=False,
    )

    objects = UserManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name"]

    class Meta:
        verbose_name = verbose_name_plural = "유저"

    def __str__(self):
        return "{}".format(self.username)

    @property
    def is_staff(self):
        return self.is_superuser


class Path(Model):
    path = models.TextField(
        verbose_name=_("알게된 경로"),
        help_text=_("알게된 경로"),
    )
