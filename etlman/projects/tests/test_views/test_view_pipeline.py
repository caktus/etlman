from http import HTTPStatus
from typing import Optional

import pytest
from django.forms.models import model_to_dict
from django.test import Client
from django.urls import reverse

from etlman.projects.models import DataInterface, Pipeline, Project, Step
from etlman.projects.tests.factories import (
    CollaboratorFactory,
    DataInterfaceFactory,
    PipelineFactory,
    StepFactory,
)


@pytest.mark.django_db
class TestMultiformStep1:
    def test_new_pipeline_with_existing_project(self, nonadmin_client, project):
        response = nonadmin_client.get(
            reverse("projects:new_pipeline", args=(project.pk,)), follow=True
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_post_data_to_new_pipeline(self, nonadmin_user, nonadmin_client, project):
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = DataInterfaceFactory()
        data = {
            "pipeline-name": pipeline.name,
            "datainterface-name": datainterface.name,
            "datainterface-interface_type": "database",
            "datainterface-connection_string": datainterface.connection_string,
        }
        response = nonadmin_client.post(
            reverse("projects:new_pipeline", args=(project.pk,)),
            data=data,
            follow=True,
        )
        assert response.status_code == HTTPStatus.OK.numerator


@pytest.mark.django_db
class TestMultiformStep2:
    def test_edit_script_view_status_code_forbidden(self, client, project):
        response = client.get(
            reverse("projects:new_step", args=(project.pk,)), follow=True
        )
        assert len(response.redirect_chain) == 1
        assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        assert response.status_code == HTTPStatus.OK.numerator
        assert "Forgot Password" in str(response.content)

    def get_response_from_post_data_to_view(
        self,
        client: Client,
        project: Project,
        step_model: Step,
        step_id: Optional[str] = None,
    ):
        data = {k: v for k, v in model_to_dict(step_model).items() if v is not None}
        url_name = "projects:edit_step" if step_id else "projects:new_step"
        kwargs = {
            "project_id": project.id,
        }
        if step_id:
            kwargs["step_id"] = step_id
        response = client.post(
            reverse(url_name, kwargs=kwargs),
            data=data,
        )
        return response

    def save_step2_data_in_session(
        self, client, pipeline, datainterface, in_transaction=None
    ):
        session = client.session
        session["data_interface"] = model_to_dict(datainterface)
        session["pipeline"] = model_to_dict(pipeline)
        if in_transaction is not None:
            session["in_transaction"] = in_transaction
        session.save()

    def test_new_step_get(self, nonadmin_client, project):
        pipeline = PipelineFactory(project=project)
        datainterface = DataInterfaceFactory(project=project)
        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)
        response = nonadmin_client.get(
            reverse("projects:new_step", args=(project.pk,)), follow=True
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_new_step_post(self, nonadmin_client, project):
        pipeline = PipelineFactory.build(project=project)
        datainterface = DataInterfaceFactory.build(project=project)
        step = StepFactory.build()

        data = {
            "name": step.name,
            "script": step.script,
            "pipeline-name": pipeline.name,
            "datainterface-name": datainterface.name,
            "datainterface-interface_type": "database",
            "datainterface-connection_string": datainterface.connection_string,
            "save": True,
        }

        self.save_step2_data_in_session(
            nonadmin_client, pipeline, datainterface, in_transaction=True
        )
        assert Pipeline.objects.count() == 0
        assert DataInterface.objects.count() == 0
        assert Step.objects.count() == 0
        assert Pipeline.objects.count() == 0

        response = nonadmin_client.post(
            reverse("projects:new_step", args=(project.pk,)),
            data=data,
        )
        assert (
            response.context is None or "form_step" not in response.context
        ), response.context["form_step"].errors
        assert response.status_code == HTTPStatus.FOUND.numerator
        assert Pipeline.objects.count() == 1
        assert DataInterface.objects.count() == 1
        assert Step.objects.count() == 1
        assert Pipeline.objects.count() == 1

        created_step = Step.objects.get()
        assert step.name == created_step.name

        created_pipeline = Pipeline.objects.get()
        assert pipeline.name == created_pipeline.name

        created_data_interface = DataInterface.objects.get()
        assert datainterface.name == created_data_interface.name
        assert datainterface.interface_type == created_data_interface.interface_type
        assert (
            datainterface.connection_string == created_data_interface.connection_string
        )

    def test_edit_step_get(self, nonadmin_client, project):
        step_model = StepFactory(pipeline=PipelineFactory(project=project))
        pipeline = step_model.pipeline
        datainterface = pipeline.input

        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)

        response = self.get_response_from_post_data_to_view(
            nonadmin_client,
            project,
            step_model,
            step_id=step_model.pk,  # make sure we use the 'edit_step' view
        )

        assert response.status_code == HTTPStatus.OK.numerator
        assert "form_step" in response.context
        assert response.context["form_step"].instance == step_model

    def test_edit_step_post(self, nonadmin_client, project):
        step_model = StepFactory(pipeline=PipelineFactory(project=project))
        pipeline = step_model.pipeline
        datainterface = pipeline.input

        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)

        data = {
            "name": "new name",
            "script": "new script",
            "save": "true",
        }
        kwargs = {"project_id": project.id, "step_id": step_model.pk}
        response = nonadmin_client.post(
            reverse("projects:edit_step", kwargs=kwargs),
            data=data,
        )
        assert (response.context is None) or (
            "form_step" not in response.context
        ), response.context["form_step"].errors
        assert response.status_code == HTTPStatus.FOUND.numerator
        edited_step_model = Step.objects.get(pk=step_model.pk)
        assert data["name"] == edited_step_model.name
        assert data["script"] == edited_step_model.script

        # html = str(response.content)
        # assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        # assert response.status_code == HTTPStatus.OK.numerator
        # assert Step.objects.count() == 1, Step.objects.all()
        # NEW_SCRIPT_CONTENT = "I am a new script"
        # step_model.script = NEW_SCRIPT_CONTENT

        # response = self.get_response_from_post_data_to_view(
        #     nonadmin_client, project, step_model, str(Step.objects.get().id)
        # )
        # html = str(response.content)
        # assert response.redirect_chain[0][-1] == HTTPStatus.FOUND.numerator
        # assert response.status_code == HTTPStatus.OK.numerator
        # assert NEW_SCRIPT_CONTENT in html
        # assert MessagesEnum.STEP_UPDATED in html
