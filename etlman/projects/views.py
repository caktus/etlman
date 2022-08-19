from denied.decorators import authorize
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from etlman.projects.authorizers import (
    user_is_authenticated,
    user_is_project_collaborator,
)
from etlman.projects.forms import ProjectForm, StepForm
from etlman.projects.models import Collaborator, Pipeline, Project, Step


class MessagesEnum:
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"
    PIPELINE_DELETED = "Pipeline {name} deleted successfully"


@authorize(user_is_authenticated)
def upsert_step(request, pk=None):
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
                reverse("projects:upsert_step", args=[saved_obj.id])
            )
    else:  # GET request
        form = StepForm(instance=loaded_obj)
    context = {"form": form}
    return render(request, "projects/upsert_step.html", context)


@authorize(user_is_project_collaborator)
def list_pipeline(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    pipelines = Pipeline.objects.filter(project=project)
    context = {"pipeline_list": pipelines, "current_project": project}
    return render(request, "projects/list_pipeline.html", context)


@authorize(user_is_project_collaborator)
def delete_pipeline(request, project_id, pipeline_id):
    pipeline = Pipeline.objects.get(id=pipeline_id)
    project = Project.objects.get(id=project_id)
    pipeline.delete()
    messages.add_message(
        request,
        messages.SUCCESS,
        MessagesEnum.PIPELINE_DELETED.format(name=pipeline.name),
    )
    return HttpResponseRedirect(reverse("projects:list_pipeline", args=(project.pk,)))


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
