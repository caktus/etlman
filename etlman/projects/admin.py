from django.contrib import admin

from .models import DataInterface, Pipeline, Projects, Step

# Register your models here.
admin.site.register(Projects)
admin.site.register(DataInterface)
admin.site.register(Pipeline)
admin.site.register(Step)