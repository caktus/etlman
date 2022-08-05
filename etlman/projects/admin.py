from django.contrib import admin

from .models import Collaborator, DataInterface, Pipeline, Project, Step


class CollaboratorInline(admin.TabularInline):
    model = Collaborator


class DataInterfaceInLine(admin.TabularInline):
    model = DataInterface


class StepInline(admin.TabularInline):
    model = Step


class ProjectAdmin(admin.ModelAdmin):
    inlines = [CollaboratorInline]
    list_display = ["name", "description"]


class DataInterfaceAdmin(admin.ModelAdmin):
    list_display = ["name", "interface_type"]
    #list_filter = ("pipeline__name",)


class PipelineAdmin(admin.ModelAdmin):
    list_display = ["name", "project"]
    list_filter = ("project__name",)
    inlines = [StepInline]


class StepAdmin(admin.ModelAdmin):
    list_display = ["name", "step_order"]
    list_filter = ("pipeline__project__name",)


admin.site.register(Project, ProjectAdmin)
admin.site.register(DataInterface, DataInterfaceAdmin)
admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(Step, StepAdmin)
