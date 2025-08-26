from django.contrib import admin
from dashboard.models.photos import SourceImage, Variant
from dashboard.models.job import Job, Execution, JobLogEntry


@admin.register(SourceImage)
class SourceImageAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SourceImage._meta.fields] + ["variant_count"]
    list_filter = ("has_variants",)
    search_fields = ("path",)
    readonly_fields = ("created_at", "updated_at")


    def variant_count(self, obj: SourceImage):
        return Variant.objects.filter(source_image=obj).count()
    


@admin.register(Variant)
class RenderedAssetAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Variant._meta.fields]
    list_filter = ("art_style","content_type","photorealist","favourite","source_quality")
    search_fields = ("path", "art_style",)
    readonly_fields = ("source_image", "created_at", "updated_at")
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Job._meta.fields]
    list_filter = ("enabled", "kind", "last_run_status")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Execution._meta.fields]
    list_filter = ("status",)
    search_fields = ("job__name", "summary")
    readonly_fields = ("created_at", "updated_at","job","started_at","finished_at","runtime_ms","summary","error","params")


@admin.register(JobLogEntry)
class JobLogEntryAdmin(admin.ModelAdmin):
    list_display = ["execution","ts","level","message","context","seq","created_at"]
    list_filter = ("level",)
    search_fields = ("message",)
    readonly_fields = ["execution","ts","level","message","context","seq","created_at"]
