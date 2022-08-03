from django.urls import path

from etlman.projects.views import new_project_wizard_view, step_form_upsert_view

app_name = "projects"
urlpatterns = [
    path("step_form/", view=step_form_upsert_view, name="step_form_upsert"),
    path("step_form/<str:pk>/", view=step_form_upsert_view, name="step_form_upsert"),
    path("add_project_wizard/", view=new_project_wizard_view, name="add_project_wizard")
]
