# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def edit_script_view(request):
    return render(request, template_name="projects/edit_script.html")
