from django.forms import ValidationError
from django.shortcuts import render

from etlman.projects.forms import StepForm
from etlman.projects.models import Step


def step_form_upsert_view(request, pk=None):

    obj = Step.objects.get(id=pk) if pk else None

    if request.method == "POST":
        print(request.POST)
        form = StepForm(request.POST, instance=obj)
        if form.is_valid():
            print("VALID")
            form.save()
        else:
            print("INVALID")

    context = {"form": StepForm()}
    return render(request, "projects/step_form.html", context)
