from http import HTTPStatus
from typing import Optional

import pytest
from django.forms import model_to_dict
from django.test import Client
from django.urls import reverse

from etlman.projects.models import Step
from etlman.projects.tests.factories import PipelineFactory, StepFactory
from etlman.projects.views import MessagesEnum


@pytest.mark.django_db
class TestScriptView:
    def test_edit_script_view_status_code_forbidden(self, client):
        response = client.get(reverse("projects:step_form_upsert"), follow=True)
        assert len(response.redirect_chain) == 1
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Forgot Password" in str(response.content)

    def test_edit_script_view_status_code_ok(self, nonadmin_client):
        response = nonadmin_client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Forgot Password" not in str(response.content)

    def test_content_of_script_is_in_HTML(self, nonadmin_client):
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.get_response_from_post_data_to_view(nonadmin_client, step_model)
        html = str(response.content)
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert step_model.script in html, html
        assert MessagesEnum.STEP_CREATED in html

    def test_update_step_in_db(self, nonadmin_client):
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.get_response_from_post_data_to_view(nonadmin_client, step_model)
        html = str(response.content)
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert Step.objects.count() == 1, Step.objects.all()
        NEW_SCRIPT_CONTENT = "I am a new script"
        step_model.script = NEW_SCRIPT_CONTENT

        response = self.get_response_from_post_data_to_view(
            nonadmin_client, step_model, str(Step.objects.get().id)
        )
        html = str(response.content)
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert NEW_SCRIPT_CONTENT in html
        assert MessagesEnum.STEP_UPDATED in html

    def test_content_of_error_in_HTML(self, nonadmin_client):
        MAX_STEP_ORDER_SIZE = 2147483647
        response = nonadmin_client.post(
            reverse("projects:step_form_upsert"),
            data={
                "name": "Testy",
                "script": "hellow",
                "pipeline": PipelineFactory.build(),
                "step_order": MAX_STEP_ORDER_SIZE + 1,
            },
        )
        assert response.status_code is HTTPStatus.OK.numerator
        assert "Ensure this value is less than or equal to 2147483647." in str(
            response.content
        )

    def test_view_new_step_creation(self, nonadmin_client):
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.get_response_from_post_data_to_view(nonadmin_client, step_model)
        html = str(response.content)
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert step_model.script in html
        assert MessagesEnum.STEP_CREATED in str(response.content)

    def get_response_from_post_data_to_view(
        self, client: Client, step_model: Step, step_id: Optional[str] = None
    ):
        data = {k: v for k, v in model_to_dict(step_model).items() if v is not None}
        response = client.post(
            reverse(
                "projects:step_form_upsert", kwargs={"pk": step_id} if step_id else None
            ),
            data=data,
            follow=True,
        )
        return response


@pytest.mark.django_db
class TestHTMLInViews:

    client = Client()

    def test_pipeline_list_view_button(self):
        response = self.client.get(reverse("projects:pipeline_list"), follow=True)
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add Pipeline" in html

    def test_pipeline_table_headers_and_tags_in_html(self):
        response = self.client.get(reverse("projects:pipeline_list"), follow=True)
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert "Name" in html
        assert "Actions" in html
        assert "<thead>" in html
        assert "<table" in html

    def test_pipeline_table_content_in_html_one_pipeline(self):
        pipeline = PipelineFactory()
        response = self.client.get(reverse("projects:pipeline_list"), follow=True)
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert pipeline.name in html
        assert pipeline.input.interface_type in html

    def test_pipeline_table_content_in_html_no_input(self):
        pipeline = PipelineFactory(input=None)
        no_data_interface_msg = "No data interface attached"
        response = self.client.get(reverse("projects:pipeline_list"), follow=True)
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert pipeline.name in html
        assert no_data_interface_msg in html
