from django.db import models
from django.utils.translation import ugettext_lazy as _

from poolink_backend.bases.models import Model


class CategoryManager(models.Manager):
    pass


class Category(Model):
    name = models.TextField(
        verbose_name=_("카테고리"),
        help_text=_("카테고리 이름입니다."),
        null=False
    )
    image = models.ImageField(
        upload_to='media',
        verbose_name=_("카테고리 이미지"),
        help_text=_("카테고리의 이미지입니다."),
        null=False
    )

    class Meta:
        verbose_name = verbose_name_plural = _("카테고리")

    def __str__(self):
        return self.name
