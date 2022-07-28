from django import forms

from .models import Step


class MonacoEditorWidget(forms.Widget):
    template_name = "projects/monaco_widget.html"


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = "__all__"
        # Customize widget for 'script' field:
        # https://stackoverflow.com/a/22250192/166053
        widgets = {
            'script': MonacoEditorWidget(),
        }
