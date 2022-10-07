import enum

from denied.decorators import authorize
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from sqlalchemy import create_engine

from etlman.projects.authorizers import (
    user_is_authenticated,
    user_is_project_collaborator,
)
from etlman.projects.forms import (
    DataInterfaceForm,
    PipelineForm,
    PipelineScheduleForm,
    ProjectForm,
    StepForm,
)
from etlman.projects.models import Collaborator, Pipeline, Project, Step


class MessagesEnum(enum.Enum):
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"
    PIPELINE_CREATED = "Pipeline '{name}' added successfully"
    PIPELINE_UPDATED = "Pipeline '{name}' updated successfully"
    PIPELINE_DELETED = "Pipeline '{name}' deleted successfully"
    PIPELINE_IN_PROGRESS_MSG = "This form contains unsaved changes"


class SessionKeyEnum(enum.Enum):
    PIPELINE = "_pipeline_wizard_pipeline_{id}"
    DATA_INTERFACE = "_pipeline_wizard_data_interface_{id}"
    STEP = "_pipeline_wizard_step_{id}"


def get_session_key(session_key_enum, object=None):
    "Generates a session key that is scoped to the object, if any."
    id_ = object.pk if object and object.pk is not None else "new"
    return session_key_enum.value.format(id=id_)


@authorize(user_is_project_collaborator)
def list_pipeline(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    pipelines = Pipeline.objects.filter(project=project)
    context = {"pipeline_list": pipelines, "current_project": project}
    return render(request, "projects/list_pipeline.html", context)


@authorize(user_is_project_collaborator)
def delete_pipeline(request, project_id, pipeline_id):
    pipeline = get_object_or_404(Pipeline, id=pipeline_id)
    project = get_object_or_404(Project, id=project_id)
    pipeline.delete()
    messages.add_message(
        request,
        messages.SUCCESS,
        MessagesEnum.PIPELINE_DELETED.value.format(name=pipeline.name),
    )
    return HttpResponseRedirect(reverse("projects:list_pipeline", args=(project.pk,)))


@authorize(user_is_project_collaborator)
def confirm_delete_pipeline(request, project_id, pipeline_id):
    pipeline = get_object_or_404(Pipeline, id=pipeline_id)
    context = {"project_id": project_id, "pipeline": pipeline}
    return render(request, "projects/confirm_delete_pipeline.html", context)


@authorize(user_is_authenticated)
def new_project(request):
    username = request.user.username

    # Form functionality
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            saved_project = form.save()
            Collaborator.objects.create(
                user=request.user,
                role="admin",
                project=saved_project,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                MessagesEnum.PROJECT_CREATED.value.format(name=saved_project.name),
            )
            return HttpResponseRedirect(
                reverse("projects:list_pipeline", args=(saved_project.pk,))
            )
    else:
        form = ProjectForm()
    context = {"form": form, "username": username}
    return render(request, "projects/new_project.html", context)


@authorize(user_is_project_collaborator)
def new_pipeline_step1(request, project_id, pipeline_id=None):
    project = get_object_or_404(Project, pk=project_id)
    loaded_pipeline = (
        get_object_or_404(Pipeline, pk=pipeline_id) if pipeline_id else None
    )
    loaded_step = loaded_pipeline.step_set.all().first() if loaded_pipeline else None
    loaded_data_interface = loaded_pipeline.input if loaded_pipeline else None
    username = request.user.username
    pipeline_session_key = get_session_key(SessionKeyEnum.PIPELINE, loaded_pipeline)
    data_interface_session_key = get_session_key(
        SessionKeyEnum.DATA_INTERFACE, loaded_data_interface
    )
    # Form functionality
    if request.method == "POST":
        form_pipeline = PipelineForm(request.POST, instance=loaded_pipeline)
        form_datainterface = DataInterfaceForm(
            request.POST, instance=loaded_data_interface
        )
        if form_pipeline.is_valid() and form_datainterface.is_valid():
            # Use session for persistence between steps in the wizard due to potential
            # size of 'script' field in step 2.
            request.session[pipeline_session_key] = form_pipeline.data
            request.session[data_interface_session_key] = form_datainterface.data
            if loaded_step:
                url = reverse("projects:edit_step", args=(project.pk, loaded_step.pk))
            else:
                url = reverse("projects:new_step", args=(project.pk,))
            return HttpResponseRedirect(url)
    else:  # GET
        session_pipeline = request.session.get(pipeline_session_key, None)
        session_data_interface = request.session.get(data_interface_session_key, None)
        form_pipeline = PipelineForm(session_pipeline, instance=loaded_pipeline)
        form_datainterface = DataInterfaceForm(
            session_data_interface,
            instance=loaded_data_interface,
            initial={"interface_type": "database"},
        )
        if session_pipeline and session_data_interface:
            messages.add_message(
                request,
                messages.WARNING,
                MessagesEnum.PIPELINE_IN_PROGRESS_MSG.value,
            )
    context = {
        "form_pipeline": form_pipeline,
        "form_datainterface": form_datainterface,
        "username": username,
        "current_project": project,
    }
    return render(request, "projects/new_pipeline.html", context)


@authorize(user_is_project_collaborator)
def new_step_step2(request, project_id, step_id=None):
    project = get_object_or_404(Project, pk=project_id)
    step = get_object_or_404(Step, pk=step_id) if step_id else None
    loaded_pipeline = step.pipeline if step else None
    loaded_data_interface = loaded_pipeline.input if loaded_pipeline else None
    pipeline_session_key = get_session_key(SessionKeyEnum.PIPELINE, loaded_pipeline)
    data_interface_session_key = get_session_key(
        SessionKeyEnum.DATA_INTERFACE, loaded_data_interface
    )
    step_session_key = get_session_key(SessionKeyEnum.STEP, step)
    session_pipeline = request.session[pipeline_session_key]
    session_data_interface = request.session[data_interface_session_key]

    # Form functionality
    if request.method == "POST":
        form_step = StepForm(request.POST, instance=step)
        form_pipeline = PipelineForm(session_pipeline, instance=loaded_pipeline)
        form_datainterface = DataInterfaceForm(
            session_data_interface, instance=loaded_data_interface
        )
        if (
            "save" in request.POST
            and form_step.is_valid()
            and form_pipeline.is_valid()
            and form_datainterface.is_valid()
        ):
            new_data_interface = form_datainterface.save(commit=False)
            new_data_interface.project = project
            new_data_interface.save()

            new_pipeline = form_pipeline.save(commit=False)
            new_pipeline.project = project
            new_pipeline.input = new_data_interface
            new_pipeline.save()

            new_step = form_step.save(commit=False)
            new_step.pipeline = new_pipeline
            new_step.step_order = 1
            new_step.save()

            if step_id:
                message = MessagesEnum.PIPELINE_UPDATED.value.format(
                    name=new_pipeline.name
                )
            else:
                message = MessagesEnum.PIPELINE_CREATED.value.format(
                    name=new_pipeline.name
                )
            messages.add_message(request, messages.SUCCESS, message)

            clear_step_wizard_session_variables(
                request,
                [pipeline_session_key, data_interface_session_key, step_session_key],
            )
            pipeline_id = new_pipeline.pk if new_pipeline.pk else form_step.instance.pk
            return HttpResponseRedirect(
                reverse(
                    "projects:schedule_pipeline",
                    args=(project.pk, pipeline_id),
                )
            )

        elif "back" in request.POST:
            request.session[step_session_key] = form_step.data
            if loaded_pipeline:
                url = reverse(
                    "projects:edit_pipeline", args=(project.pk, loaded_pipeline.pk)
                )
            else:
                url = reverse("projects:new_pipeline", args=(project.pk,))
            return HttpResponseRedirect(url)
    else:  # GET
        initial = request.session.get(step_session_key)
        # if initial is provided to a ModelForm with an attached instance,
        # it will override the values on the instance.
        # https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/#providing-initial-values
        if initial is None and step is None:
            initial = {
                "name": session_pipeline["pipeline-name"] + "_script",
                "script": "def main():\n\t...\nif __name__ == '__main__':\n\tmain()",
            }
        form_step = StepForm(instance=step, initial=initial)

    context = {
        "form_step": form_step,
        "project": project,
    }
    return render(request, "projects/new_step.html", context)


def clear_step_wizard_session_variables(request, session_keys):
    """Iterates over session keys and clears cache"""
    for session_key in session_keys:
        request.session.pop(session_key, None)


@authorize(user_is_project_collaborator)
def clear_step_wizard_session_view(request, project_id, pipeline_id=None):
    project = get_object_or_404(Project, pk=project_id)
    loaded_pipeline = (
        get_object_or_404(Pipeline, pk=pipeline_id) if pipeline_id else None
    )
    loaded_data_interface = loaded_pipeline.input if loaded_pipeline else None
    pipeline_session_key = get_session_key(SessionKeyEnum.PIPELINE, loaded_pipeline)
    data_interface_session_key = get_session_key(
        SessionKeyEnum.DATA_INTERFACE, loaded_data_interface
    )
    clear_step_wizard_session_variables(
        request, [pipeline_session_key, data_interface_session_key]
    )
    return HttpResponseRedirect(reverse("projects:list_pipeline", args=(project.pk,)))


@authorize(user_is_project_collaborator)
@require_http_methods(["POST"])
def test_db_connection_string(request, project_id):
    data_columns, data_table = [], []
    success, message = False, ""
    form = DataInterfaceForm(request.POST)
    if form.is_valid():
        try:
            success = True
            engine = create_engine(form.cleaned_data["connection_string"])
            conn = engine.connect()
            cursor = conn.exec_driver_sql(form.cleaned_data["sql_query"])
            # Using a blanket except statement because we do not know
            # what database driver the user is using.
        except Exception as e:
            success = False
            message = f"We were unable to connect to the database. \n {e}"
        if success:
            message = "Database connection successful!"
            data_columns = [desc[0] for desc in cursor.cursor.description]
            data_table = cursor.fetchmany(20)
    context = {
        "data_columns": data_columns,
        "data_table": data_table,
        "success": success,
        "message": message,
        "form": form,
    }
    return render(request, "projects/_test_connection.html", context)


@authorize(user_is_project_collaborator)
@require_http_methods(["POST"])
def test_step_connection_string(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = StepForm(request.POST)
    if form.is_valid():
        step = form.save(commit=False)
        status_code, stdout, stderr = step.run_script()
        if status_code == 0:
            message = "Script ran successfully!"
        else:
            message = "Script failed!"
    else:
        message = "Form contains invalid field(s)!"  # TBD
        status_code, stdout, stderr = None, None, None
    context = {
        "message": message,
        "form": form,
        "project": project,
        "success": status_code == 0,
        "status_code": status_code,
        "stderr": stderr,
        "stdout": stdout,
    }
    return render(request, "projects/_test_script.html", context)


@authorize(user_is_project_collaborator)
def schedule_pipeline_runtime(request, project_id, pipeline_id):
    project = get_object_or_404(Project, pk=project_id)
    pipeline = get_object_or_404(Pipeline, pk=pipeline_id)
    # Safely check for existence of related object:
    # https://stackoverflow.com/a/40743258/166053
    if hasattr(pipeline, "schedule"):
        pipeline_schedule = pipeline.schedule
    else:
        pipeline_schedule = None
    if request.method == "POST":
        form = PipelineScheduleForm(request.POST, instance=pipeline_schedule)
        if form.is_valid():
            schedule_form = form.save(commit=False)
            schedule_form.pipeline = pipeline
            schedule_form.save()
            return HttpResponseRedirect(
                reverse("projects:list_pipeline", args=(project.pk,))
            )

    else:
        form = PipelineScheduleForm(
            instance=pipeline_schedule,
            initial={"time_zone": settings.TIME_ZONE}
            if pipeline_schedule is None
            else None,
        )
    context = {"form": form, "project": project, "pipeline": pipeline}
    return render(request, "projects/schedule_pipeline.html", context)
