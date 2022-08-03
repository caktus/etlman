from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from etlman.projects.forms import ProjectForm, StepForm
from etlman.projects.models import Collaborator, Step


class MessagesEnum:
    STEP_UPDATED = "Step updated"
    STEP_CREATED = "New step script added succesfully"


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
    else:  # GET
        form = StepForm(instance=loaded_obj)
    context = {"form": form}
    return render(request, "projects/step_form.html", context)


def new_project_wizard_view(request):
    # Get username
    username = None
    if request.user.is_authenticated:
        username = request.user.username

    # Form functionality
    if request.method == "POST":
        form = ProjectForm(request.POST)
        # New projects require the logged user as collaborators
        # Here we instanantiate Collaborator and and assign the
        # current user as the "collaborators".
        collaborator_user_object = Collaborator.objects.create(
            user=request.user, role="admin", project="???"
        )
        form.data.user = collaborator_user_object
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("home"))
    form = ProjectForm()
    context = {"form": form, "username": username}
    return render(request, "projects/add_project_wizard.html", context)
