from django.urls import path

from etlman.projects.views import edit_script_view, step_form_view

# from etlman.projects.views import user_detail_view, user_redirect_view, user_update_view

app_name = "projects"
urlpatterns = [
    path("monaco", view=edit_script_view, name="monaco"),
    path("step_form", view=step_form_view, name="step_form"),
    ]
