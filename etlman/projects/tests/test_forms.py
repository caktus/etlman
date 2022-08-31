import pytest

from etlman.projects.forms import StepForm
from etlman.projects.tests.factories import PipelineFactory, StepFactory


@pytest.mark.django_db
class TestScriptForm:
    def test_django_form_fields(self):
        sf = StepFactory.build(pipeline=PipelineFactory())
        form = StepForm(
            data={
                "name": sf.name,
                "script": sf.script,
            }
        )
        assert form.is_valid(), form.errors  # is valid automatically calls valid_data
        saved_obj = form.save(commit=False)
        assert sf.name == saved_obj.name
        assert sf.script == saved_obj.script
