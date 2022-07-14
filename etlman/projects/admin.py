from django.contrib import admin

from .models import DataInterface, Pipeline, Project, Step

# Register your models here.
admin.site.register(Project)
admin.site.register(DataInterface)
admin.site.register(Pipeline)
admin.site.register(Step)
