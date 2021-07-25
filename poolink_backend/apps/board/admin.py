from django.contrib import admin

from poolink_backend.apps.board.models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("user", "id", "name", "bio", "like_count", "scrap_count")
