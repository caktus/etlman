from django.urls import path

from etlman.projects.views import (
    new_project_view,
    pipeline_delete,
    pipeline_list,
    step_form_upsert_view,
)

app_name = "projects"
urlpatterns = [
    path("new-project/", view=new_project_view, name="new_project"),
    path("<int:project_id>/pipelines/", view=pipeline_list, name="pipeline_list"),
    path(
        "<int:project_id>/delete-pipeline/<int:pipeline_id>",
        view=pipeline_delete,
        name="pipeline_delete",
    ),
    path("step-form/", view=step_form_upsert_view, name="step_form_upsert"),
    path("step-form/<str:pk>/", view=step_form_upsert_view, name="step_form_upsert"),
]
