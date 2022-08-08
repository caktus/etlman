from denied.authorizers import any_authorized
from denied.decorators import authorize
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from etlman.projects.forms import ProjectForm, StepForm
from etlman.projects.models import Collaborator, Step, Pipeline


class MessagesEnum:
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"
    PROJECT_CREATED = "Project {name} added successfully"


@authorize(any_authorized)
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


def pipeline_list(request):
    pipelines = Pipeline.objects.all()
    context = {"pipeline_list": pipelines}
    return render(request, "projects/pipeline_list.html", context)


@authorize(any_authorized)  # any logged in user
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
            return HttpResponseRedirect(reverse("home"))

    form = ProjectForm()
    context = {"form": form, "username": username}
    return render(request, "projects/new_project.html", context)
