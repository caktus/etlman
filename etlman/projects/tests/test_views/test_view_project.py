from http import HTTPStatus

import pytest
from django.urls import reverse

from etlman.projects.models import Project
from etlman.projects.tests.factories import ProjectFactory
from util import (
    get_anon_client,
    get_authenticated_client,
    get_authenticated_client_and_test_user,
)


@pytest.mark.django_db
class TestNewProjectView:
    def test_add_project_wizard_status_code_with_anon(self):
        client = get_anon_client()
        response = client.get(reverse("projects:add_project_wizard"), follow=True)
        assert response.status_code == HTTPStatus.OK.numerator

    def test_add_project_wizard_status_code_with_user(self):
        client = get_authenticated_client()
        response = client.get(reverse("projects:add_project_wizard"))
        assert response.status_code == HTTPStatus.OK.numerator

    def test_add_project_wizard_post_with_added_collaborator(self):
        client, user = get_authenticated_client_and_test_user()
        project_data = ProjectFactory.build()
        data = {"name": project_data.name, "description": project_data.description}
        response = client.post(
            reverse("projects:add_project_wizard"),
            data=data,
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator
        assert Project.objects.count() == 1, Project.objects.all()
        assert Project.objects.get().collaborator_set.get().user == user
