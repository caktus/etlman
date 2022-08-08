from django.urls import path

from etlman.projects.views import new_project_view, pipeline_list, step_form_upsert_view

app_name = "projects"
urlpatterns = [
    path("step_form/", view=step_form_upsert_view, name="step_form_upsert"),
    path("step_form/<str:pk>/", view=step_form_upsert_view, name="step_form_upsert"),
    path("pipeline_list/", view=pipeline_list, name="pipeline_list"),
    path("new-project/", view=new_project_view, name="new_project"),
]
