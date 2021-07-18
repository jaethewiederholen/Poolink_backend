from django.db import models
from django.utils.translation import ugettext_lazy as _

from poolink_backend.apps.category.models import Category
from poolink_backend.apps.users.models import User
from poolink_backend.bases.models import Model


class BoardManager(models.Manager):
    pass


class Board(Model):
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("보드 소유자"),
        on_delete=models.CASCADE,
        related_name="boards",
    )

    name = models.CharField(
        verbose_name=_("보드 이름"),
        help_text=_("보드의 이름입니다"),
        null=False,
        default="이름없는 보드",
        max_length=255,
    )
    image = models.ImageField(
        upload_to='media',
        verbose_name=_("보드 이미지"),
        help_text=_("유저가 설정한 보드 이미지입니다."),
        null=True,
        blank=True,
    )
    bio = models.TextField(
        verbose_name=_("보드 설명"),
        help_text=_("보드에 대한 설명입니다"),
        null=True,
    )
    charge = models.BooleanField(
        verbose_name=_("유료보드 설정 여부"),
        help_text=_("유료 보드인지를 나타냅니다. MVP 단계에서 사용되지 않습니다."),
        null=False,
        default=False,
    )
    like = models.ManyToManyField(User, related_name="like", null=True,)
    scrap = models.ManyToManyField(User, related_name="scrap", null=True,)
    category = models.ManyToManyField(Category, related_name="board_category", null=True,)

    class Meta:
        verbose_name = verbose_name_plural = _("보드")
        ordering = ['-id']

    @property
    def like_count(self):
        return self.like.count()

    @property
    def scrap_count(self):
        return self.scrap.count()

    def __str__(self):
        return self.name
