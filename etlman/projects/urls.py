from django.urls import path

from etlman.projects.views import (
    clear_step_wizard_session_view,
    confirm_delete_pipeline,
    delete_pipeline,
    list_pipeline,
    new_pipeline_step1,
    new_project,
    new_step_step2,
    schedule_pipeline_runtime,
    test_db_connection_string,
    test_step_connection_string,
)

app_name = "projects"

urlpatterns = [
    path("new-project/", view=new_project, name="new_project"),
    path("<int:project_id>/pipelines/", view=list_pipeline, name="list_pipeline"),
    path(
        "<int:project_id>/delete-pipeline/<int:pipeline_id>/",
        view=delete_pipeline,
        name="delete_pipeline",
    ),
    path(
        "<int:project_id>/confirm-delete-pipeline/<int:pipeline_id>/",
        view=confirm_delete_pipeline,
        name="confirm_delete_pipeline",
    ),
    path(
        "<int:project_id>/new-pipeline/", view=new_pipeline_step1, name="new_pipeline"
    ),
    path(
        "<int:project_id>/edit-pipeline/<int:pipeline_id>/",
        view=new_pipeline_step1,
        name="edit_pipeline",
    ),
    path("<int:project_id>/new-step/", view=new_step_step2, name="new_step"),
    path(
        "<int:project_id>/edit-step/<int:step_id>/",
        view=new_step_step2,
        name="edit_step",
    ),
    path(
        "<int:project_id>/test-connection/",
        view=test_db_connection_string,
        name="test_connection",
    ),
    path(
        "<int:project_id>/clear-wizard-session/<int:pipeline_id>/",
        view=clear_step_wizard_session_view,
        name="clear_wizard_session",
    ),
    path(
        "<int:project_id>/clear-wizard-session/",
        view=clear_step_wizard_session_view,
        name="clear_wizard_session",
    ),
    path(
        "<int:project_id>/step-test/",
        view=test_step_connection_string,
        name="step_test",
    ),
    path(
        "<int:project_id>/schedule/<int:pipeline_id>/",
        view=schedule_pipeline_runtime,
        name="schedule_pipeline",
    ),
]
