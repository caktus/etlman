from http import HTTPStatus

import pytest
from django.forms.models import model_to_dict
from django.urls import reverse

from etlman.projects.models import DataInterface
from etlman.projects.tests.factories import (
    CollaboratorFactory,
    DataInterfaceFactory,
    PipelineFactory,
    ProjectFactory,
    StepFactory,
)


@pytest.mark.django_db
class TestMultiformStep1:
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


@pytest.mark.django_db
class TestMultiformStep2:
    def test_new_step_with_existing_project(self, nonadmin_user, nonadmin_client):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = DataInterfaceFactory()
        session = nonadmin_client.session
        session["data_interface"] = model_to_dict(datainterface)
        session["pipeline"] = model_to_dict(pipeline)
        session.save()
        response = nonadmin_client.get(
            reverse("projects:new_step", args=(project.pk,)), follow=True
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_post_data_to_new_step(self, nonadmin_user, nonadmin_client):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = DataInterfaceFactory()
        step = StepFactory()

        data = {
            "name": [pipeline.name, datainterface.name],
            "interface_type": ["database"],
            "connection_string": [datainterface.connection_string],
            "script": step.script,
        }

        session = nonadmin_client.session
        session["data_interface"] = model_to_dict(datainterface)
        session["pipeline"] = model_to_dict(pipeline)
        session.save()

        response = nonadmin_client.post(
            reverse("projects:new_step", args=(project.pk,)),
            data=data,
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_post_data_to_new_step_with_transaction(
        self, nonadmin_user, nonadmin_client
    ):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = DataInterfaceFactory()

        session = nonadmin_client.session
        session["data_interface"] = model_to_dict(datainterface)
        session["pipeline"] = model_to_dict(pipeline)
        session["in_transaction"] = True
        session.save()

        response = nonadmin_client.get(
            reverse("projects:new_pipeline", args=(project.pk,)),
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_save_button_on_step_form(self, nonadmin_user, nonadmin_client):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface_build = DataInterfaceFactory(project=project)
        datainterface = DataInterface(
            name=datainterface_build.name,
            connection_string=datainterface_build.connection_string,
            project=datainterface_build.project,  # this here doesn't work
        )
        step = StepFactory()

        data = {
            "name": [pipeline.name, datainterface.name],
            "interface_type": ["database"],
            "connection_string": [datainterface.connection_string],
            "script": step.script,
            "save": True,
        }

        session = nonadmin_client.session
        session["data_interface"] = model_to_dict(datainterface)
        session["pipeline"] = model_to_dict(pipeline)
        session["in_transaction"] = True
        session.save()

        response = nonadmin_client.post(
            reverse("projects:new_step", args=(project.pk,)),
            data=data,
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_cancel_button_on_step_form(self, nonadmin_user, nonadmin_client):
        project = ProjectFactory()
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = DataInterfaceFactory()
        step = StepFactory()

        data = {
            "name": [pipeline.name, datainterface.name],
            "interface_type": ["database"],
            "connection_string": [datainterface.connection_string],
            "script": step.script,
            "cancel": True,
        }

        session = nonadmin_client.session
        session["data_interface"] = model_to_dict(datainterface)
        session["pipeline"] = model_to_dict(pipeline)
        session["in_transaction"] = True
        session.save()

        response = nonadmin_client.post(
            reverse("projects:new_step", args=(project.pk,)),
            data=data,
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator
