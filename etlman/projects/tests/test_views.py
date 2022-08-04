from http import HTTPStatus
from typing import Optional

import pytest
from django.forms import model_to_dict
from django.test import Client
from django.urls import reverse

from etlman.projects.models import Project, Step
from etlman.projects.tests.factories import PipelineFactory, ProjectFactory, StepFactory
from etlman.projects.views import MessagesEnum
from etlman.users.models import User


@pytest.mark.django_db
class TestScriptView:

    client = Client()

    def test_edit_script_view_status_code_forbidden(self):
        response = self.client.get(reverse("projects:step_form_upsert"), follow=True)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Forgot Password" in str(response.content)

    def test_edit_script_view_status_code_ok(self):
        self.__authorize_user()
        response = self.client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Forgot Password" not in str(response.content)

    def test_content_of_script_is_in_HTML(self):
        self.__authorize_user()
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.__get_response_from_post_data_to_view(step_model)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator, html
        assert step_model.script in html
        assert MessagesEnum.STEP_CREATED in html

    def test_update_step_in_db(self):
        """
        - GET for existing object - 200 status code, content of script appears in HTML
        - POST for new object with valid data returns redirect, saved to DB
        - POST for existing object with valid data returns redirect, updates saved to DB
        """
        self.__authorize_user()
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.__get_response_from_post_data_to_view(step_model)
        html = str(response.content)

        assert Step.objects.count() == 1, html
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
        self.__authorize_user()
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
        self.__authorize_user()
        step_model = StepFactory.build(pipeline=PipelineFactory())
        response = self.__get_response_from_post_data_to_view(step_model)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert step_model.script in html
        assert MessagesEnum.STEP_CREATED in str(response.content)

    def __authorize_user(self):
        user, _ = User.objects.get_or_create(username="testuser")
        self.client.force_login(user)

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
class TestNewProjectView:

    client = Client()

    def test_add_project_wizard_status_code_with_anon(self):
        response = self.client.get(reverse("projects:add_project_wizard"), follow=True)
        assert response.status_code == HTTPStatus.OK.numerator

    def test_add_project_wizard_status_code_with_user(self):
        self.__authorize_user()
        response = self.client.get(reverse("projects:add_project_wizard"))
        assert response.status_code == HTTPStatus.OK.numerator

    def test_add_project_wizard_post_with_added_collaborator(self):
        user = self.__authorize_user()
        project_data = ProjectFactory.build()
        data = {"name": project_data.name, "description": project_data.description}
        response = self.client.post(
            reverse("projects:add_project_wizard"),
            data=data,
            follow=True,
        )
        assert Project.objects.count() == 1, Project.objects.all()
        assert response.status_code == HTTPStatus.OK.numerator
        assert Project.objects.get().collaborator_set.last().user == user

    def __authorize_user(self):
        user, _ = User.objects.get_or_create(username="testuser")
        self.client.force_login(user)
        return user
