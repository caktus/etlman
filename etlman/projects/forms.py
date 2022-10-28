from django import forms

from .models import DataInterface, Pipeline, PipelineSchedule, Project, Step


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
        labels = {"name": "Pipeline name"}


class DataInterfaceForm(forms.ModelForm):
    prefix = "data_interface"

    class Meta:
        model = DataInterface
        fields = ["name", "interface_type", "connection_string", "sql_query"]
        labels = {"name": "Data interface name", "sql_query": "SQL query"}
        widgets = {
            "connection_string": forms.Textarea(attrs={"rows": 3}),
        }


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["name", "language", "script"]
        # Customize widget for 'script' field:
        # https://stackoverflow.com/a/22250192/166053
        widgets = {
            "script": MonacoEditorWidget(),
            "language": forms.Select(),
        }


class PipelineScheduleForm(forms.ModelForm):
    class Meta:
        model = PipelineSchedule
        fields = [
            "start_date",
            "start_time",
            "time_zone",
            "interval",
            "unit",
            "published",
        ]
        widgets = {
            "start_date": forms.TextInput(attrs={"placeholder": "YYYY-MM-DD"}),
            "start_time": forms.TextInput(attrs={"placeholder": "00:00:00"}),
        }
