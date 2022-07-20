from re import template
from django.shortcuts import render
from etlman.projects.forms import StepForm
from django.contrib import messages
from etlman.projects.models import Step


def edit_script_view(request):
    data = request.data
    if request.method == "POST":
        if data.script_id:  # Updates step
            # TODO: Check if all fields are filled and/or the 'Edit' function pre-filled the form controls
            obj = Step.objects.get(id=data.script_id)
            obj.name = data.name
            obj.script = data.script
        else:  # Creates a new step
            obj = Step.objects.create()
            obj.name = data.name
            obj.script = data.script
            Step.save(obj)

    return render(request, template_name="projects/edit_script.html")

def step_form_view(request):
    step_form = StepForm()
    return render(request, "projects/step_form.html", context={'step_form': step_form})
