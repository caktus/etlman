import pytest
from django.test import Client, TestCase
from django.urls import reverse

from etlman.projects.context_processor import currrent_user_projects
from etlman.projects.models import Project
from etlman.projects.tests.factories import ProjectFactory
from etlman.users.models import User


def get_anon_client():
    return Client()


def get_authenticated_client():
    client, _ = get_authenticated_client_and_test_user()
    return client


def get_authenticated_client_and_test_user():
    client = get_anon_client()
    user, _ = User.objects.get_or_create(username="testuser")
    client.force_login(user)
    return client, user


@pytest.mark.django_db
class UserProjects(TestCase):
    @pytest.mark.django_db
    def test_list_user_with_projects(self):
        client, user = get_authenticated_client_and_test_user()
        request = self.client.get(reverse("home"))

        project_data = ProjectFactory.build()
        data = {"name": project_data.name, "description": project_data.description}
        response = self.client.post(
            reverse("projects:add_project_wizard"),
            data=data,
            follow=True,
        )
        assert response != "something"
        assert currrent_user_projects(request) == 1

    def test_list_user_without_projects(self):
        client, user = get_authenticated_client_and_test_user()
        response = self.client.get("home")
        assert Project.objects.all().filter(collaborator_set__contains=user) == 0
        assert response != "something"
