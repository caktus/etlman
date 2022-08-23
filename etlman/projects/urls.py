from django.urls import path

from etlman.projects.views import (
    confirm_delete_pipeline,
    delete_pipeline,
    list_pipeline,
    new_project,
    upsert_step,
)

app_name = "projects"
urlpatterns = [
    path("new-project/", view=new_project, name="new_project"),
    path("<int:project_id>/pipelines/", view=list_pipeline, name="list_pipeline"),
    path(
        "<int:project_id>/delete-pipeline/<int:pipeline_id>",
        view=delete_pipeline,
        name="delete_pipeline",
    ),
    path(
        "<int:project_id>/confirm-delete-pipeline/<int:pipeline_id>",
        view=confirm_delete_pipeline,
        name="confirm_delete_pipeline",
    ),
    path("upsert-step/", view=upsert_step, name="upsert_step"),
    path("upsert-step/<str:pk>/", view=upsert_step, name="upsert_step"),
]
