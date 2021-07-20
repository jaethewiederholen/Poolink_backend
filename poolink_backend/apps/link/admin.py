from django.contrib import admin

from poolink_backend.apps.link.models import Link


@admin.register(Link)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "board_id", "label", "url", "show")

