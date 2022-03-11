from django.db import models
from django.utils.translation import ugettext_lazy as _

from poolink_backend.bases.models import Model


# Create your models here.
class Hashtag(Model):
    name = models.CharField(
        verbose_name=_("태그이름"),
        help_text=_("태그 이름입니다."),
        null=False,
        max_length=100,
    )

    class Meta:
        verbose_name = verbose_name_plural = _("해시태그")

    def __str__(self):
        return self.name
