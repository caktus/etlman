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
from etlman.projects.models import Collaborator, DataInterface, Pipeline, Project, Step


class MessagesEnum:
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"
    PIPELINE_CREATED = "Pipeline '{name}' added successfully"
    PIPELINE_DELETED = "Pipeline '{name}' deleted successfully"


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
            # New projects require the logged user as a collaborator
            # Here we assigned the current user as the "collaborator".
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
def new_pipeline_step1(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    username = request.user.username
    if request.method == "POST":
        form_pipeline = PipelineForm(request.POST)
        form_datainterface = DataInterfaceForm(request.POST)
        if form_pipeline.is_valid() and form_datainterface.is_valid():
            filled_datainterface = form_datainterface.save(commit=False)
            filled_datainterface.name = request.POST["datainterface-name"]
            request.session["data_interface"] = model_to_dict(filled_datainterface)

            filled_pipeline = form_pipeline.save(commit=False)
            filled_pipeline.name = request.POST["pipeline-name"]
            filled_pipeline.input_id = filled_datainterface.pk
            request.session["pipeline"] = model_to_dict(filled_pipeline)

            return HttpResponseRedirect(
                reverse("projects:new_step", args=(project.pk,))
            )
    else:  # GET
        pipeline_auxiliary = request.session.get("pipeline", None)
        datainterface_auxiliary = request.session.get("data_interface", None)
        form_pipeline = PipelineForm(initial=pipeline_auxiliary)
        form_datainterface = DataInterfaceForm(initial=datainterface_auxiliary)

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
    form_data_interface = request.session["data_interface"]
    form_pipeline = request.session["pipeline"]

    # Form functionality
    if request.method == "POST":
        form_step = NewStepForm(request.POST, instance=step)
        if "save" in request.POST and form_step.is_valid():

            # New Data Interface
            saved_data_interface = DataInterface.objects.create(
                project=project,
                name=form_data_interface["name"],
                interface_type=form_data_interface["interface_type"],
                connection_string=form_data_interface["connection_string"],
            )

            # New Pipeline
            saved_pipeline = Pipeline.objects.create(
                project=project,
                name=form_pipeline["name"],
                input=saved_data_interface,
            )

            # New Step
            form_step.save(commit=False)
            saved_step = Step.objects.create(
                pipeline=saved_pipeline,
                name=request.POST["name"],
                script=request.POST["script"],
                step_order=1,
            )

            # So this here should be always Step 1 for now
            # When this changes, use the code below to calculte next step order
            # step_order=max(Step.objects.values_list('step_order', flat=True)) + 1
            # if Step.objects.exists()
            # else 1,

            saved_step.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                MessagesEnum.PIPELINE_CREATED.format(name=saved_pipeline.name),
            )

            clear_step_wizard_session_variables(request)
            return HttpResponseRedirect(
                reverse("projects:pipeline_list", args=(project.pk,))
            )
        elif "cancel" in request.POST:
            filled_step = form_step.save(commit=False)
            filled_step.name = request.POST["name"]
            filled_step.script = request.POST["script"]
            request.session["step"] = model_to_dict(filled_step)
            return HttpResponseRedirect(
                reverse("projects:new_pipeline", args=(project.pk,))
            )
    else:  # GET
        form_step = NewStepForm(
            instance=step,
            initial={
                "name": form_pipeline["name"] + "_script",
                "script": "def main():\n\t...\nif __name__ == '__main__':\n\tmain()",
            },
        )
    context = {"form_step": form_step, "project": project}
    return render(request, "projects/new_step.html", context)


def clear_step_wizard_session_variables(request):
    for object_name in ["pipeline", "data_interface", "step"]:
        request.session[object_name] = None
