from django.contrib import admin

from .models import (
    Collaborator,
    DataInterface,
    Pipeline,
    PipelineRun,
    PipelineSchedule,
    Project,
    Step,
)


class CollaboratorInline(admin.TabularInline):
    model = Collaborator


class DataInterfaceInLine(admin.TabularInline):
    model = DataInterface


class StepInline(admin.TabularInline):
    model = Step


class ProjectAdmin(admin.ModelAdmin):
    inlines = [CollaboratorInline, DataInterfaceInLine]
    list_display = ["name", "description"]


class DataInterfaceAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "interface_type"]
    list_filter = ("project__name",)


class PipelineAdmin(admin.ModelAdmin):
    list_display = ["name", "project"]
    list_filter = ("project__name",)
    inlines = [
        StepInline,
    ]


class StepAdmin(admin.ModelAdmin):
    list_display = ["name", "step_order"]
    list_filter = ("pipeline__project__name",)


class PipelineScheduleAdmin(admin.ModelAdmin):
    list_display = ["pipeline", "start_date", "start_time", "published"]
    list_filter = ("published",)


class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ["pipeline", "started_at", "ended_at", "output"]
    list_filter = ("started_at", "ended_at")


admin.site.register(Project, ProjectAdmin)
admin.site.register(DataInterface, DataInterfaceAdmin)
admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(PipelineSchedule, PipelineScheduleAdmin)
admin.site.register(PipelineRun, PipelineRunAdmin)
