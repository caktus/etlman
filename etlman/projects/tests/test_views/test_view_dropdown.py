from html import unescape
from http import HTTPStatus
from random import randint

import pytest
from django.urls import reverse
from django_celery_beat.models import PeriodicTask

from etlman.projects.models import Collaborator, Pipeline, PipelineSchedule, Step
from etlman.projects.tests.factories import (
    CollaboratorFactory,
    PipelineFactory,
    PipelineScheduleFactory,
    ProjectFactory,
    StepFactory,
)
from etlman.projects.views import MessagesEnum
from etlman.users.models import User


@pytest.mark.django_db
class TestProjectDropdownList:
    def test_dropdown_empty(self, nonadmin_client):
        response = nonadmin_client.get(reverse("home"))
        html = unescape(response.content.decode("utf-8"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html

    def test_dropdown_with_one_project(self, nonadmin_client):
        project_data = ProjectFactory.build()
        data = {"name": project_data.name, "description": project_data.description}
        response = nonadmin_client.post(
            reverse("projects:new_project"),
            data=data,
        )
        response = nonadmin_client.get(reverse("home"))
        html = unescape(response.content.decode("utf-8"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert project_data.name in html

    def test_dropdown_with_several_projects(self, nonadmin_client):
        project_list = ProjectFactory.build_batch(randint(2, 5))
        for project_data in project_list:
            data = {"name": project_data.name, "description": project_data.description}
            response = nonadmin_client.post(
                reverse("projects:new_project"),
                data=data,
            )
        response = nonadmin_client.get(reverse("home"))
        html = unescape(response.content.decode("utf-8"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert all([project_data.name in html for project_data in project_list])

    def test_dropdown_context_processor(self, nonadmin_client, nonadmin_user):
        saved_project = ProjectFactory.create()
        CollaboratorFactory.create(project=saved_project, user=nonadmin_user)
        assert Collaborator.objects.count() > 0

        response = nonadmin_client.get(reverse("home"))
        context = response.context
        project_list = context["current_user_projects"]
        assert response.status_code == HTTPStatus.OK.numerator
        assert saved_project in project_list, context

        nonadmin_client.force_login(
            User.objects.create(username="new_test_user", password="foobar")
        )

        response = nonadmin_client.get(reverse("home"))
        context = response.context
        project_list = context["current_user_projects"]
        assert response.status_code == HTTPStatus.OK.numerator
        assert saved_project not in project_list, context["user"]

    def test_delete_pipeline(self, nonadmin_client, nonadmin_user):
        """
        The pipeline delete view deletes the pipeline and its related models.
        """
        saved_project = ProjectFactory.create()
        CollaboratorFactory.create(project=saved_project, user=nonadmin_user)
        pipeline = PipelineFactory(project=saved_project)
        PipelineScheduleFactory(pipeline=pipeline)
        StepFactory(pipeline=pipeline)
        # PeriodicTask should be created by the PipelineSchedule.save() method
        assert PeriodicTask.objects.count() == 1
        response = nonadmin_client.post(
            reverse(
                "projects:delete_pipeline",
                args=(
                    saved_project.id,
                    pipeline.id,
                ),
            ),
            follow=True,
        )

        html = unescape(response.content.decode("utf-8"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert (
            MessagesEnum.PIPELINE_DELETED.value.format(name=pipeline.name) in html
        ), html
        assert Pipeline.objects.count() == 0
        assert PipelineSchedule.objects.count() == 0
        assert PeriodicTask.objects.count() == 0
        assert Step.objects.count() == 0

    def test_confirm_delete_pipeline(self, nonadmin_client, nonadmin_user):
        saved_project = ProjectFactory.create()
        CollaboratorFactory.create(project=saved_project, user=nonadmin_user)
        pipeline = PipelineFactory(project=saved_project)
        response = nonadmin_client.post(
            reverse(
                "projects:confirm_delete_pipeline",
                args=(
                    saved_project.id,
                    pipeline.id,
                ),
            ),
            follow=True,
        )
        delete_msg = f'Do you really want to delete Pipeline "{ pipeline.name }"?'
        html = unescape(response.content.decode("utf-8"))
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Delete" in html
        assert "Cancel" in html
        assert delete_msg in html, html
