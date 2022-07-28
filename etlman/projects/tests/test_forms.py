from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from etlman.projects.forms import StepForm
from etlman.projects.tests.factories import StepFactory, PipelineFactory


@pytest.mark.django_db
class TestEditScriptViewAndForm:

    client = Client()

    def test_django_form_is_valid(self):
        sf = StepFactory.build(pipeline=PipelineFactory())
        form = StepForm(
            data={
                "name": sf.name,
                "script": sf.script,
                "pipeline": sf.pipeline,
                "step_order": sf.step_order,
            }
        )
        assert form.is_valid(), form.errors

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
        assert form.is_valid(), form.errors  # is valid automatically calls valid_data, so data is valid
        form.save()
        assert sf.name == form.data["name"]
        assert sf.script == form.data["script"]
        assert sf.step_order == form.data["step_order"]
        assert sf.pipeline == form.data["pipeline"]

    def test_django_form_not_valid_duplicate_step_order(self):
        # Test to write:
        # - Create a Step and save it to the DB
        # - Try to create a step in the same pipeline with a duplicate step_order
        # - Check that the error exists per:
        # https://adamj.eu/tech/2020/06/15/how-to-unit-test-a-django-form/#unit-tests
        pass
