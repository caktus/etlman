from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Collaborator,
    DataInterface,
    Pipeline,
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


class PipelineHistoryAdmin(SimpleHistoryAdmin):
    list_display = ["name", "project"]
    history_list_display = ["status"]
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


admin.site.register(Project, ProjectAdmin)
admin.site.register(DataInterface, DataInterfaceAdmin)
admin.site.register(Pipeline, PipelineHistoryAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(PipelineSchedule, PipelineScheduleAdmin)
