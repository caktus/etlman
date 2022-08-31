from django import forms

from .models import DataInterface, Pipeline, Project, Step


class MonacoEditorWidget(forms.Widget):
    template_name = "projects/monaco_widget.html"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]


class PipelineForm(forms.ModelForm):
    prefix = "pipeline"

    class Meta:
        model = Pipeline
        fields = ["name"]
        labels = {"name": "Pipeline Name"}


class DataInterfaceForm(forms.ModelForm):
    prefix = "data_interface"

    class Meta:
        model = DataInterface
        fields = ["name", "interface_type", "connection_string"]
        labels = {"name": "Data Interface Name"}


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["name", "script"]
        # Customize widget for 'script' field:
        # https://stackoverflow.com/a/22250192/166053
        widgets = {
            "script": MonacoEditorWidget(),
        }
