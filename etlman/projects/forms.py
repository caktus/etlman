from django import forms

from .models import DataInterface, Pipeline, Project, Step


class MonacoEditorWidget(forms.Widget):
    template_name = "projects/monaco_widget.html"


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = "__all__"
        # Customize widget for 'script' field:
        # https://stackoverflow.com/a/22250192/166053
        widgets = {
            "script": MonacoEditorWidget(),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]


class PipelineForm(forms.ModelForm):
    class Meta:
        model = Pipeline
        fields = ["name"]
        labels = {"name": "Pipeline Name"}


class DataInterfaceForm(forms.ModelForm):
    class Meta:
        model = DataInterface
        fields = ["name", "interface_type", "connection_string"]
        labels = {"name": "Data Interface Name"}


class NewStepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["name", "script"]
        # Customize widget for 'script' field:
        # https://stackoverflow.com/a/22250192/166053
        widgets = {
            "script": MonacoEditorWidget(),
        }
