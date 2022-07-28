import pytest

from etlman.projects.forms import StepForm
from etlman.projects.tests.factories import PipelineFactory, StepFactory


@pytest.mark.django_db
class TestEditScriptViewAndForm:
    def test_django_form_fields(self):
        sf = StepFactory.build(pipeline=PipelineFactory())
        form = StepForm(
            data={
                "name": sf.name,
                "script": sf.script,
                "pipeline": sf.pipeline,
                "step_order": sf.step_order,
            }
        )
        assert (
            form.is_valid()
        ), form.errors  # is valid automatically calls valid_data, so data is valid
        saved_obj = form.save()
        assert sf.name == saved_obj.name
        assert sf.script == saved_obj.script
        assert sf.step_order == saved_obj.step_order
        assert sf.pipeline == saved_obj.pipeline

    def test_django_form_not_valid_duplicate_step_order(self):
        # Test to write:
        # - Create a Step and save it to the DB
        # - Try to create a step in the same pipeline with a duplicate step_order
        # - Check that the error exists per:
        # https://adamj.eu/tech/2020/06/15/how-to-unit-test-a-django-form/#unit-tests
        pass
