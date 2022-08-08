from http import HTTPStatus
from random import randint

import pytest
from django.urls import reverse

from etlman.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
class TestProjectDropdownList:
    def test_dropdown_empty(self, nonadmin_client):
        response = nonadmin_client.get(reverse("home"))
        html = str(response.content)
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
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert project_data.name in html

    def test_dropdown_with_many_projects(self, nonadmin_client):
        project_list = ProjectFactory.build_batch(randint(1, 10))
        for project_data in project_list:
            data = {"name": project_data.name, "description": project_data.description}
            response = nonadmin_client.post(
                reverse("projects:new_project"),
                data=data,
            )
        response = nonadmin_client.get(reverse("home"))
        html = str(response.content)
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Add a project" in html, html
        assert all([project_data.name in html for project_data in project_list])

    # def test_dropdown_with_many_projects_without_other_user_projects(self, nonadmin_client):
    #     client1 = get_authenticated_client("testuser")
    #     project_list = ProjectFactory.build_batch(randint(1, 10))
    #     for project_data in project_list:
    #         data = {"name": project_data.name, "description": project_data.description}
    #         response = client1.post(
    #             reverse("projects:new_project"),
    #             data=data,
    #         )

    #     client2 = get_authenticated_client("anotheruser")
    #     response = client2.get(reverse("home"))
    #     html = str(response.content)
    #     assert response.status_code == HTTPStatus.OK.numerator
    #     assert "Add a project" in html, html
    #     assert not any([project_data.name in html for project_data in project_list])

    #     response = client1.get(reverse("home"))
    #     html = str(response.content)
    #     assert "Add a project" in html, html
    #     assert all([project_data.name in html for project_data in project_list])
