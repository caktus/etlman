import enum

from denied.decorators import authorize
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from sqlalchemy import create_engine

from etlman.projects.authorizers import (
    user_is_authenticated,
    user_is_project_collaborator,
)
from etlman.projects.forms import DataInterfaceForm, PipelineForm, ProjectForm, StepForm
from etlman.projects.models import Collaborator, Pipeline, Project, Step


class MessagesEnum(enum.Enum):
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"
    PIPELINE_CREATED = "Pipeline '{name}' added successfully"
    PIPELINE_UPDATED = "Pipeline '{name}' updated successfully"
    PIPELINE_DELETED = "Pipeline '{name}' deleted successfully"


class SessionKeyEnum(enum.Enum):
    PIPELINE = "_pipeline_wizard_pipeline"
    DATA_INTERFACE = "_pipeline_wizard_data_interface"
    STEP = "_pipeline_wizard_step"


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

    # Form functionality
    if request.method == "POST":
        form_pipeline = PipelineForm(request.POST, instance=loaded_pipeline)
        form_datainterface = DataInterfaceForm(
            request.POST, instance=loaded_data_interface
        )
        if form_pipeline.is_valid() and form_datainterface.is_valid():
            # Use session for persistence between steps in the wizard due to potential
            # size of 'script' field in step 2.
            request.session[SessionKeyEnum.PIPELINE.value] = form_pipeline.data
            request.session[
                SessionKeyEnum.DATA_INTERFACE.value
            ] = form_datainterface.data
            if loaded_step:
                url = reverse("projects:edit_step", args=(project.pk, loaded_step.pk))
            else:
                url = reverse("projects:new_step", args=(project.pk,))
            return HttpResponseRedirect(url)
    else:  # GET
        session_pipeline = request.session.get(SessionKeyEnum.PIPELINE.value, None)
        session_data_interface = request.session.get(
            SessionKeyEnum.DATA_INTERFACE.value, None
        )
        form_pipeline = PipelineForm(session_pipeline, instance=loaded_pipeline)
        form_datainterface = DataInterfaceForm(
            session_data_interface, instance=loaded_data_interface
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
    session_data_interface = request.session[SessionKeyEnum.DATA_INTERFACE.value]
    session_pipeline = request.session[SessionKeyEnum.PIPELINE.value]

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

            clear_step_wizard_session_variables(request)
            return HttpResponseRedirect(
                reverse("projects:list_pipeline", args=(project.pk,))
            )

        elif "back" in request.POST:
            request.session[SessionKeyEnum.STEP.value] = form_step.data
            if loaded_pipeline:
                url = reverse(
                    "projects:edit_pipeline", args=(project.pk, loaded_pipeline.pk)
                )
            else:
                url = reverse("projects:new_pipeline", args=(project.pk,))
            return HttpResponseRedirect(url)
    else:  # GET
        initial = request.session.get(SessionKeyEnum.STEP.value) or {
            "name": session_pipeline["pipeline-name"] + "_script",
            "script": "def main():\n\t...\nif __name__ == '__main__':\n\tmain()",
        }
        form_step = StepForm(instance=step, initial=initial)

    context = {
        "form_step": form_step,
        "project": project,
    }
    return render(request, "projects/new_step.html", context)


def clear_step_wizard_session_variables(request):
    for session_key in SessionKeyEnum:
        request.session.pop(session_key.value, None)


@authorize(user_is_project_collaborator)
def test_connection(request, project_id):
    # Probably use form or something here for validation?
    # print(request.POST["data_interface-connection_string"])
    connection_string = request.POST["data_interface-connection_string"]
    # For example, connect to our own DB
    # pg_engine = create_engine(connection_string)
    try:
        pg_engine = create_engine(connection_string)
        success = True
    except Exception as e:
        success = False
        message = str(e)
        table_names = ""
    if success:
        message = "Connected!"
        pg_engine.connect()
        table_names = pg_engine.table_names()
    context = {
        "table_names": table_names,
        "success": success,
        "message": message,
    }
    return render(request, "projects/test_connection.html", context)
