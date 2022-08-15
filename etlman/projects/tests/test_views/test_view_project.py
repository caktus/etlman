from http import HTTPStatus

import pytest
from django.urls import reverse

from etlman.projects.models import Project
from etlman.projects.tests.factories import ProjectFactory
from etlman.projects.views import MessagesEnum


@pytest.mark.django_db
class TestNewProjectView:
    def test_new_project_status_code_with_anon(self, client):
        response = client.get(reverse("projects:new_project"), follow=True)
        assert len(response.redirect_chain) == 1
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator

    def test_new_project_status_code_with_user(self, nonadmin_client):
        response = nonadmin_client.get(reverse("projects:new_project"), follow=True)
        assert not response.redirect_chain
        assert response.status_code == HTTPStatus.OK.numerator

    def test_new_project_post_with_added_collaborator(
        self, nonadmin_client, nonadmin_user
    ):
        project_data = ProjectFactory.build()
        data = {"name": project_data.name, "description": project_data.description}
        response = nonadmin_client.post(
            reverse("projects:new_project"),
            data=data,
            follow=True,
        )
        html = str(response.content)
        assert len(response.redirect_chain) == 1
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert Project.objects.count() == 1, Project.objects.all()
        assert Project.objects.get().collaborator_set.get().user == nonadmin_user
        assert MessagesEnum.PROJECT_CREATED.format(name=project_data.name) in html
