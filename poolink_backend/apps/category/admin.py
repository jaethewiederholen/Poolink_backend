from django.contrib import admin

from poolink_backend.apps.category.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
