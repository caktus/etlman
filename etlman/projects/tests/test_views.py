from http import HTTPStatus
from typing import Optional

import pytest
from django.forms import model_to_dict
from django.test import Client
from django.urls import reverse

from etlman.projects.models import Step
from etlman.projects.tests.factories import PipelineFactory, StepFactory
from etlman.projects.views import MessagesEnum
from etlman.users.models import User


@pytest.mark.django_db
class TestScriptView:

    client = Client()

    def test_edit_script_view_status_code(self):
        # TODO: start blocking users that are not authenticated
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator

    def test_content_of_script_is_in_HTML(self):
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.__get_response_from_post_data_to_view(step_model)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert step_model.script in html
        assert MessagesEnum.STEP_CREATED in html

    def test_update_step_in_db(self):
        """
        - GET for existing object - 200 status code, content of script appears in HTML
        - POST for new object with valid data returns redirect, saved to DB
        - POST for existing object with valid data returns redirect, updates saved to DB
        """
        step_model = StepFactory.build(pipeline=PipelineFactory())
        self.__get_response_from_post_data_to_view(step_model)

        NEW_SCRIPT_CONTENT = "I am a new script"
        step_model.script = NEW_SCRIPT_CONTENT

        response = self.__get_response_from_post_data_to_view(
            step_model, str(Step.objects.last().id)
        )
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert NEW_SCRIPT_CONTENT in html
        assert MessagesEnum.STEP_UPDATED in html

    def test_content_of_error_in_HTML(self):
        """
        - POST with invalid data - error appears in HTML
        """

        MAX_STEP_ORDER_SIZE = 2147483647
        response = self.client.post(
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

    def test_view_new_step_creation(self):
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.__get_response_from_post_data_to_view(step_model)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert step_model.script in html
        assert MessagesEnum.STEP_CREATED in str(response.content)

    def __get_response_from_post_data_to_view(
        self, step_model: Step, step_id: Optional[str] = None
    ):
        data = {k: v for k, v in model_to_dict(step_model).items() if v is not None}
        response = self.client.post(
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
