from django import forms

from .models import Step


class MonacoEditorWidget(forms.Widget):
    template_name = "projects/monaco_widget.html"


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        exclude = ["script"]

    script = forms.CharField(widget=MonacoEditorWidget)
