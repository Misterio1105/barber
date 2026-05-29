from django.contrib import admin

from .models import MasterComment


@admin.register(MasterComment)
class MasterCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "master", "text", "created_at")
    search_fields = ("text", "user__username", "master__name", "master__surname")
    list_filter = ("master", "created_at")
