from django.urls import path

from etlman.projects.views import (
    new_pipeline_step1,
    new_project_view,
    new_step_step2,
    pipeline_list,
    step_form_upsert_view,
)

app_name = "projects"

urlpatterns = [
    path("new-project/", view=new_project_view, name="new_project"),
    path("step-form/", view=step_form_upsert_view, name="step_form_upsert"),
    path("step-form/<str:pk>/", view=step_form_upsert_view, name="step_form_upsert"),
    path("<int:project_id>/pipelines/", view=pipeline_list, name="pipeline_list"),
    path(
        "<int:project_id>/new-pipeline/", view=new_pipeline_step1, name="new_pipeline"
    ),
    path("<int:project_id>/new-step/", view=new_step_step2, name="new_step"),
]
