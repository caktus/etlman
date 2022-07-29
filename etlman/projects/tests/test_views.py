from http import HTTPStatus
from django.forms import model_to_dict

import pytest
from django.test import Client
from django.urls import reverse

from etlman.projects.forms import StepForm
from etlman.projects.models import Pipeline, Project, Step
from etlman.projects.tests.factories import PipelineFactory, ProjectFactory, StepFactory
from etlman.projects.views import MessagesEnum


@pytest.mark.django_db
class TestScriptView:

    client = Client()

    def test_edit_script_view_status_code(self):
        response = self.client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator

    def test_content_of_script_is_in_HTML(self):
        # GET for existing object - 200 status code, content of script appears in HTML
        # POST for new object with valid data returns redirect, saved to DB
        data = model_to_dict(StepFactory.build(pipeline=PipelineFactory()))
        response = self.client.post(reverse("projects:step_form_upsert"), data=data)
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert data["script"] in html
        assert MessagesEnum.STEP_CREATED in html

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

        new_script_content = "I am a new script"

        response = self.client.post(
            reverse("projects:step_form_upsert", kwargs={"pk": saved_object.id}),
            data={"script": new_script_content},
        )
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert new_script_content in html
        assert MessagesEnum.STEP_UPDATED in html

    def test_content_of_error_in_HTML(self):
        # POST with invalid data - error appears in HTML
        MAX_STEP_ORDER_SIZE = 2147483647
        StepFactory(pipeline=PipelineFactory(project=ProjectFactory()))
        data = {
            "name": "Testy",
            "script": "hellow",
            "pipeline": Pipeline.objects.last(),
            "step_order": MAX_STEP_ORDER_SIZE + 1,
        }
        response = self.client.post(reverse("projects:step_form_upsert"), data=data)
        assert response.status_code is HTTPStatus.OK.numerator
        assert "Ensure this value is less than or equal to 2147483647." in str(
            response.content
        )

    def test_view_new_step_creation(self):
        data = model_to_dict(StepFactory(pipeline=PipelineFactory()))
        response = self.client.post(reverse("projects:step_form_upsert"), data=data)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert data["script"] in html
        assert MessagesEnum.STEP_CREATED in str(response.content)
