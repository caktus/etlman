from http import HTTPStatus

import pytest
from django.urls import reverse

from etlman.projects.tests.factories import (
    CollaboratorFactory,
    DataInterfaceFactory,
    PipelineFactory,
    ProjectFactory,
)


@pytest.mark.django_db
class TestNewProjectView:
    # def test_new_pipeline_without_project(self, nonadmin_client):
    #     project_object = ProjectFactory()
    #     response = nonadmin_client.get(
    #         reverse("projects:new_pipeline", args=(project_object.pk,)), follow=True
    #     )
    #     assert len(response.redirect_chain) == 0
    #     assert response.status_code == HTTPStatus.FORBIDDEN.numerator

    def test_new_pipeline_with_existing_project(self, nonadmin_user, nonadmin_client):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        response = nonadmin_client.get(
            reverse("projects:new_pipeline", args=(project.pk,)), follow=True
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_post_data_to_new_pipeline(self, nonadmin_user, nonadmin_client):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = DataInterfaceFactory()
        data = {
            "name": [pipeline.name, datainterface.name],
            "interface_type": ["database"],
            "connection_string": [datainterface.connection_string],
        }
        response = nonadmin_client.post(
            reverse("projects:new_pipeline", args=(project.pk,)),
            data=data,
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator
