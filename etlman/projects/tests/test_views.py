from http import HTTPStatus

import pytest
from django.test import Client, TestCase
from django.urls import reverse

from etlman.projects.forms import StepForm
from etlman.projects.tests.factories import PipelineFactory, StepFactory


@pytest.mark.django_db
class TestEditScriptViewAndForm(TestCase):

    client = Client()

    def test_edit_script_view_status_code(self):
        response = self.client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator

    def test_content_of_script_is_HTML(self):
        # GET for existing object - 200 status code, content of script appears in HTML
        # POST for new object with valid data returns redirect, saved to DB
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
        saved_object = form.save()
        response = self.client.get(
            reverse("projects:step_form_upsert", kwargs={"pk": saved_object.id})
        )
        assert response.status_code == HTTPStatus.OK.numerator
        assert saved_object.script in str(response.content)

    def test_update_step_in_db(self):
        # GET for existing object - 200 status code, content of script appears in HTML
        # POST for new object with valid data returns redirect, saved to DB
        # POST for existing object with valid data returns redirect, updates saved to DB
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
        saved_object = form.save()
        response = self.client.get(
            reverse("projects:step_form_upsert", kwargs={"pk": saved_object.id})
        )

        assert response.status_code == HTTPStatus.OK.numerator

        response = self.client.post(
            reverse("projects:step_form_upsert", kwargs={"pk": saved_object.id}),
            data={"script": "I am a new script"},
        )

        assert response.status_code == HTTPStatus.OK.numerator
        assert "I am a new script" in str(response.content)

    def test_content_of_error_in_HTML(self):
        # POST with invalid data - error appears in HTML
        sf = StepFactory.build(pipeline=PipelineFactory())
        MAX_STEP_ORDER_SIZE = 2147483647
        data = {
            "name": sf.name,
            "script": sf.script,
            "pipeline": sf.pipeline,
            "step_order": MAX_STEP_ORDER_SIZE + 1,
        }
        response = self.client.post(reverse("projects:step_form_upsert"), data=data)
        assert response.status_code is HTTPStatus.OK.numerator
        assert "Ensure this value is less than or equal to 2147483647." in str(
            response.content
        )
