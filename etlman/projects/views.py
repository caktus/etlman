from denied.decorators import authorize
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from etlman.projects.authorizers import (
    user_is_authenticated,
    user_is_project_collaborator,
)
from etlman.projects.forms import DataInterfaceForm, PipelineForm, ProjectForm, StepForm
from etlman.projects.models import Collaborator, Pipeline, Project, Step


class MessagesEnum:
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"
    PIPELINE_CREATED = "Pipeline '{name}' added successfully"


@authorize(user_is_authenticated)
def step_form_upsert_view(request, pk=None):
    loaded_obj = Step.objects.get(id=pk) if pk else None
    if request.method == "POST":
        form = StepForm(request.POST, instance=loaded_obj)
        if form.is_valid():

            saved_obj = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                MessagesEnum.STEP_UPDATED if loaded_obj else MessagesEnum.STEP_CREATED,
            )
            return HttpResponseRedirect(
                reverse("projects:step_form_upsert", args=[saved_obj.id])
            )
    else:  # GET request
        form = StepForm(instance=loaded_obj)
    context = {"form": form}
    return render(request, "projects/step_form.html", context)


@authorize(user_is_authenticated)
def new_project_view(request):
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
                reverse("projects:pipeline_list", args=(saved_project.pk,))
            )

    form = ProjectForm()
    context = {"form": form, "username": username}
    return render(request, "projects/new_project.html", context)


@authorize(user_is_project_collaborator)
def pipeline_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    pipelines = Pipeline.objects.filter(project=project)
    context = {"pipeline_list": pipelines, "current_project": project}
    return render(request, "projects/pipeline_list.html", context)


@authorize(user_is_project_collaborator)
def new_pipeline(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    username = request.user.username

    # Form functionality
    if request.method == "POST":
        form_pipeline = PipelineForm(request.POST)
        form_datainterface = DataInterfaceForm(request.POST)
        if form_pipeline.is_valid() and form_datainterface.is_valid():

            saved_datainterface = form_datainterface.save(commit=False)
            saved_datainterface.name = request.POST.getlist("name")[-1]
            saved_datainterface.project_id = project_id
            saved_datainterface.save()

            saved_pipeline = form_pipeline.save(commit=False)
            saved_pipeline.name = request.POST.getlist("name")[0]
            saved_pipeline.project_id = project_id
            saved_pipeline.input_id = saved_datainterface.pk
            saved_pipeline.save()

            # messages.add_message(
            #     request,
            #     messages.SUCCESS,
            #     MessagesEnum.PIPELINE_CREATED.format(name=saved_pipeline.name),
            # )

            return HttpResponseRedirect(reverse("home"))
            # return HttpResponseRedirect(
            #     reverse("projects:step_form_upsert", args=(project_id,))
            # )
    else: # GET
        form_pipeline, form_datainterface = PipelineForm(), DataInterfaceForm()
    context = {
        "form_pipeline": form_pipeline,
        "form_datainterface": form_datainterface,
        "username": username,
        "current_project": project,
    }
    return render(request, "projects/new_pipeline.html", context)
