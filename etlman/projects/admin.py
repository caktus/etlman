from django.contrib import admin

from .models import Collaborator, DataInterface, Pipeline, Project, Step


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


# Register your models here.
admin.site.register(Project, ProjectAdmin)
admin.site.register(DataInterface, DataInterfaceAdmin)
admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(Step)
