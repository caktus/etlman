from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from etlman.projects.forms import StepForm
from etlman.projects.tests.factories import StepFactory


@pytest.mark.django_db
class TestEditScriptViewAndForm:

    client = Client()

    def test_django_form_is_valid(self):
        sf = StepFactory.build()
        form = StepForm(
            data={
                "name": sf.name,
                "script": sf.script,
                "pipeline": sf.pipeline,
                "step_order": sf.step_order,
            }
        )
        assert bool(form.is_valid) is True

    def test_django_form_fields(self):
        sf = StepFactory.build()
        form = StepForm(
            data={
                "name": sf.name,
                "script": sf.script,
                "pipeline": sf.pipeline,
                "step_order": sf.step_order,
            }
        )
        form.is_valid()  # is valid automatically calls valid_data, so data is valid
        assert sf.name == form.data["name"]
        assert sf.script == form.data["script"]
        assert sf.step_order == form.data["step_order"]
        assert sf.pipeline == form.data["pipeline"]

    def test_edit_script_view_status_code(self):
        response = self.client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator