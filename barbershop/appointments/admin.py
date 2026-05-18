from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "master",
        "service",
        "date",
        "time",
        "status",
        "created_at",
    )
    list_filter = ("status", "date", "master")
    search_fields = (
        "user__username",
        "master__name",
        "master__surname",
        "service__name",
    )
    list_editable = ("status",)
    date_hierarchy = "date"
    ordering = ("-date", "-time")
