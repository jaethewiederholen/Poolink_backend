from django.db import models
from django.utils.translation import ugettext_lazy as _

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
        verbose_name=_("보드 이미지"),
        help_text=_("유저가 설정한 보드 이미지입니다."),
        null=True,
        # upload_to=UploadTo()
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
    like_count = models.IntegerField(
        verbose_name=_("좋아요 수"), help_text=_("보드의 좋아요 수를 나타냅니다.")
    )
    scrap_count = models.IntegerField(
        verbose_name=_("스크랩 수"), help_text=_("보드가 스크랩 된 수를 나타냅니다.")
    )

    class Meta:
        verbose_name = verbose_name_plural = _("보드")

    def __str__(self):
        return self.name
