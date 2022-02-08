from django.contrib import admin

from poolink_backend.apps.notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "notification", "board", "created")
