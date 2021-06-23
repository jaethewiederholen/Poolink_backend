from django.contrib import admin

from poolink_backend.apps.board.models import Board


@admin.register(Board)
class BoardAdmin(admin):
    list_display = ("name", "email")
