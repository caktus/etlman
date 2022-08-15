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
    StepForm,
)
from etlman.projects.models import Collaborator, DataInterface, Pipeline, Project, Step


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
def new_pipeline_step1(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    username = request.user.username
    {
        "data_interface": request.session.get("data_interface", None),
        "pipeline": request.session.get("pipeline", None),
        "project_id": request.session.get("project", None),
    }

    # Form functionality
    if request.method == "POST":
        form_pipeline = PipelineForm(request.POST)
        form_datainterface = DataInterfaceForm(request.POST)
        if form_pipeline.is_valid() and form_datainterface.is_valid():

            request.session["project_id"] = project.id

            filled_datainterface = form_datainterface.save(commit=False)
            # 'request.POST.getlist("name")[-1]' is the content linked
            # to the DataInterface model.
            filled_datainterface.name = request.POST.getlist("name")[-1]
            filled_datainterface.project_id = project_id
            request.session["data_interface"] = model_to_dict(filled_datainterface)

            filled_pipeline = form_pipeline.save(commit=False)
            # 'request.POST.getlist("name")[0]' is the content linked
            # to the Pipeline model.
            filled_pipeline.name = request.POST.getlist("name")[0]
            filled_pipeline.project_id = project_id
            filled_pipeline.input_id = filled_datainterface.pk
            request.session["pipeline"] = model_to_dict(filled_pipeline)

            if not request.session["step"]:
                request.session["step"] = {
                    "name": filled_datainterface.name + "_script",
                    "script": "def main():\n\t...\nif __name__ == '__main__':\n\tmain()",
                }

            return HttpResponseRedirect(
                reverse("projects:new_step", args=(project.pk,))
            )
    else:  # GET
        if all([key in request.session for key in ["data_interface", "pipeline"]]):
            form_pipeline = PipelineForm(initial=request.session["pipeline"])
            form_datainterface = DataInterfaceForm(
                initial=request.session["data_interface"]
            )
        else:
            form_pipeline, form_datainterface = PipelineForm(), DataInterfaceForm()
    context = {
        "form_pipeline": form_pipeline,
        "form_datainterface": form_datainterface,
        "username": username,
        "current_project": project,
    }
    return render(request, "projects/new_pipeline.html", context)


@authorize(user_is_project_collaborator)
def new_step_step2(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form_data_interface = request.session["data_interface"]
    form_pipeline = request.session["pipeline"]

    # Form functionality
    if request.method == "POST":
        form_step = NewStepForm(request.POST)
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
                step_order=Step.objects.all().last().step_order + 1,
            )
            saved_step.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                MessagesEnum.PIPELINE_CREATED.format(name=saved_pipeline.name),
            )

            request.session["pipeline"] = None
            request.session["data_interface"] = None
            request.session["step"] = None
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
        form_step = (
            NewStepForm(initial=request.session["step"])
            if "step" in request.session
            else NewStepForm()
        )
    context = {"form_step": form_step, "project": project}
    return render(request, "projects/new_step.html", context)
