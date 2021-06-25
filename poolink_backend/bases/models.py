import timeago
from annoying.fields import AutoOneToOneField as _AutoOneToOneField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class AutoOneToOneField(_AutoOneToOneField):
    pass


class Manager(models.Manager):
    pass


class AvailableManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class UpdateMixin(object):
    def update(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=kwargs.keys())


class Model(UpdateMixin, TimeStampedModel, models.Model):

    remark = models.TextField(blank=True, null=True, verbose_name="비고")

    is_active = models.BooleanField("활성화 여부", default=True, blank=True, null=True)

    class Meta:
        abstract = True

    objects = Manager()
    available = AvailableManager()

    @property
    def time(self):
        return timeago.format(self.created, timezone.now(), "ko")

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self._meta.get_field("created").verbose_name = _("생성일")
        self._meta.get_field("modified").verbose_name = _("수정일")
