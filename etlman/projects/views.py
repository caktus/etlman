from denied.decorators import authorize
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from etlman.projects.authorizers import (
    user_is_authenticated,
    user_is_project_collaborator,
)
from etlman.projects.forms import (
    DataInterfaceForm,
    NewStepForm,
    PipelineForm,
    ProjectForm,
)
from etlman.projects.models import Collaborator, Pipeline, Project, Step


class MessagesEnum:
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"
    PIPELINE_CREATED = "Pipeline '{name}' added successfully"
    PIPELINE_DELETED = "Pipeline '{name}' deleted successfully"


class SessionKeyEnum:
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
        MessagesEnum.PIPELINE_DELETED.format(name=pipeline.name),
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
            # New projects require the logged user as a collaborator.
            Collaborator.objects.create(
                user=request.user,
                role="admin",
                project=saved_project,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                MessagesEnum.PROJECT_CREATED.format(name=saved_project.name),
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
    loaded_data_interface = loaded_pipeline.input if loaded_pipeline else None
    username = request.user.username

    # Form functionality
    if request.method == "POST":
        form_pipeline = PipelineForm(
            request.POST, instance=loaded_pipeline, prefix="pipeline"
        )
        form_datainterface = DataInterfaceForm(
            request.POST, instance=loaded_data_interface, prefix="data_interface"
        )
        if form_pipeline.is_valid() and form_datainterface.is_valid():
            request.session[
                SessionKeyEnum.DATA_INTERFACE
            ] = form_datainterface.cleaned_data
            request.session[SessionKeyEnum.PIPELINE] = form_pipeline.cleaned_data

            return HttpResponseRedirect(
                reverse("projects:new_step", args=(project.pk,))
            )
    else:  # GET
        # pipeline_auxiliary = request.session.get("pipeline", None)
        # datainterface_auxiliary = request.session.get("data_interface", None)
        form_pipeline = PipelineForm(instance=loaded_pipeline, prefix="pipeline")
        form_datainterface = DataInterfaceForm(
            instance=loaded_data_interface, prefix="data_interface"
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
    session_data_interface = request.session[SessionKeyEnum.DATA_INTERFACE]
    session_pipeline = request.session[SessionKeyEnum.PIPELINE]

    # Form functionality
    if request.method == "POST":
        form_step = NewStepForm(request.POST, instance=step)
        # Don't pass prefix into these forms, because we are passing in the
        # cleaned_data from step 1.
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

            messages.add_message(
                request,
                messages.SUCCESS,
                MessagesEnum.PIPELINE_CREATED.format(name=new_pipeline.name),
            )

            clear_step_wizard_session_variables(request)
            return HttpResponseRedirect(
                reverse("projects:list_pipeline", args=(project.pk,))
            )

        elif "back" in request.POST:
            filled_step = form_step.save(commit=False)
            filled_step.name = request.POST["name"]
            filled_step.script = request.POST["script"]
            request.session["step"] = model_to_dict(filled_step)
            return HttpResponseRedirect(
                reverse("projects:new_pipeline", args=(project.pk,))
            )
    else:  # GET
        initial = request.session.get("step") or {
            "name": session_pipeline["name"] + "_script",
            "script": "def main():\n\t...\nif __name__ == '__main__':\n\tmain()",
        }
        form_step = NewStepForm(instance=step, initial=initial)
    context = {"form_step": form_step, "project": project}
    return render(request, "projects/new_step.html", context)


def clear_step_wizard_session_variables(request):
    for object_name in ["pipeline", "data_interface", "step"]:
        request.session[object_name] = None
