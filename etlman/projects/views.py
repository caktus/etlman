from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from etlman.projects.forms import StepForm
from etlman.projects.models import Step


def step_form_upsert_view(request, pk=None):  # GET

    loaded_obj = Step.objects.get(id=pk) if pk else None
    if request.method == "POST":
        form = StepForm(request.POST, instance=loaded_obj)
        if form.is_valid():
            saved_obj = form.save()
            messages.add_message(request, messages.SUCCESS, "New step script added succesfully!" if loaded_obj is None else "Step updated!")
            return HttpResponseRedirect(
                reverse("projects:step_form_upsert", args=[saved_obj.id])
            )
        else:
            messages.add_message(request, messages.ERROR, form.errors)

    context = {"form": StepForm(instance=loaded_obj)}
    return render(request, "projects/step_form.html", context)
