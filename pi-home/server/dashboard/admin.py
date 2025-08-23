from django.contrib import admin
from .models.application import SourceImage, RenderedAsset
from .models.job import Job, Execution, JobLogEntry


@admin.register(SourceImage)
class SourceImageAdmin(admin.ModelAdmin):
    list_display = ("id", "path", "created_at", "updated_at")
    search_fields = ("path",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(RenderedAsset)
class RenderedAssetAdmin(admin.ModelAdmin):
    list_display = ("id", "path", "art_style", "source_image", "created_at", "updated_at")
    list_filter = ("art_style",)
    search_fields = ("art_style",)
    readonly_fields = ("created_at", "updated_at")
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "kind",
        "cron",
        "enabled",
        "last_run_status",
        "last_run_started_at",
        "last_run_finished_at",
    )
    list_filter = ("enabled", "kind", "last_run_status")
    search_fields = ("name", "kind")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "status",
        "started_at",
        "finished_at",
        "runtime_ms",
        "created_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("job__name", "summary")
    readonly_fields = ("created_at", "updated_at")


@admin.register(JobLogEntry)
class JobLogEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "execution", "seq", "level", "ts", "message")
    list_filter = ("level",)
    search_fields = ("message",)
    readonly_fields = ("created_at", "updated_at")
