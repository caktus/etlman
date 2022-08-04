from http import HTTPStatus
from random import randint

import pytest
from django.urls import reverse

from etlman.projects.tests.factories import ProjectFactory
from util import get_authenticated_client


@pytest.mark.django_db
class TestProjectDropdownList:
    def test_dropdown_empty(self):
        client = get_authenticated_client()
        response = client.get(reverse("home"), follow=True)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html

    def test_dropdown_with_one_project(self):
        client = get_authenticated_client()
        project_data = ProjectFactory.build()
        data = {"name": project_data.name, "description": project_data.description}
        response = client.post(
            reverse("projects:add_project_wizard"),
            data=data,
            follow=True,
        )
        response = client.get(reverse("home"), follow=True)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert project_data.name in html

    def test_dropdown_with_many_projects(self):
        client = get_authenticated_client()
        project_list = ProjectFactory.build_batch(randint(1, 10))
        for project_data in project_list:
            data = {"name": project_data.name, "description": project_data.description}
            response = client.post(
                reverse("projects:add_project_wizard"),
                data=data,
                follow=True,
            )
        response = client.get(reverse("home"), follow=True)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert all([project_data.name in html for project_data in project_list])

    def test_dropdown_with_many_projects_without_other_user_projects(self):
        client1 = get_authenticated_client("testuser")
        project_list = ProjectFactory.build_batch(randint(1, 10))
        for project_data in project_list:
            data = {"name": project_data.name, "description": project_data.description}
            response = client1.post(
                reverse("projects:add_project_wizard"),
                data=data,
                follow=True,
            )

        client2 = get_authenticated_client("anotheruser")
        response = client2.get(reverse("home"), follow=True)
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert not any([project_data.name in html for project_data in project_list])

        response = client1.get(reverse("home"), follow=True)
        html = str(response.content)
        assert all([project_data.name in html for project_data in project_list])
