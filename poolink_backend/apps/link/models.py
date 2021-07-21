from django.db import models
from django.utils.translation import ugettext_lazy as _

from poolink_backend.apps.board.models import Board
from poolink_backend.bases.models import Model


class LinkManager(models.Manager):
    pass


class Link(Model):
    board = models.ForeignKey(
        Board,
        verbose_name=_("상위 보드"),
        on_delete=models.CASCADE,
        related_name="links",
    )

    label = models.CharField(
        verbose_name=_("링크 라벨링"),
        help_text=_("링크의 라벨입니다"),
        null=False,
        max_length=255,
    )
    url = models.URLField(
        verbose_name=_("링크 주소"),
        help_text=_("링크의 url 주소입니다."),
        null=False,
    )
    alarm = models.DateTimeField(null=True, blank=True)
    show = models.BooleanField(
        verbose_name=_("링크 공개 여부"),
        help_text=_("링크의 공개 여부를 나타냅니다."),
        null=False,
        default=True,
    )
    favicon = models.URLField(
        verbose_name=_("링크 파비콘"),
        help_text=_("링크의 파비콘(favicon)입니다."),
        null=True,
        blank=True,
    )
    meta_image = models.URLField(
        verbose_name=_("링크 미리보기 이미지"),
        help_text=_("링크의 미리보기 이미지입니다."),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = verbose_name_plural = _("링크")
        ordering = ['-id']

    def __str__(self):
        return self.label
