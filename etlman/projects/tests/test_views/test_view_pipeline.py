from http import HTTPStatus

import pytest
from django.urls import reverse

from etlman.projects.forms import DataInterfaceForm, PipelineForm
from etlman.projects.models import DataInterface, Pipeline, Step
from etlman.projects.tests.factories import (
    CollaboratorFactory,
    DataInterfaceFactory,
    PipelineFactory,
    StepFactory,
)
from etlman.projects.views import SessionKeyEnum


@pytest.mark.django_db
class TestMultiformStep1:
    def test_new_pipeline_with_existing_project(self, nonadmin_client, project):
        response = nonadmin_client.get(
            reverse("projects:new_pipeline", args=(project.pk,)), follow=True
        )
        assert response.status_code == HTTPStatus.OK.numerator

    def test_post_data_to_new_pipeline(self, nonadmin_user, nonadmin_client, project):
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory.build()
        datainterface = pipeline.input
        data = {
            "pipeline-name": pipeline.name,
            "data_interface-name": datainterface.name,
            "data_interface-interface_type": "database",
            "data_interface-connection_string": datainterface.connection_string,
        }
        response = nonadmin_client.post(
            reverse("projects:new_pipeline", args=(project.pk,)), data=data
        )
        assert response.status_code == HTTPStatus.FOUND.numerator, (
            "Pipeline form errors: "
            + str(response.context["form_pipeline"].errors)
            + "\nData interface form errors: "
            + str(response.context["form_datainterface"].errors)
        )
        # Check session for saved values
        assert (
            nonadmin_client.session[SessionKeyEnum.PIPELINE.value]["pipeline-name"]
            == data["pipeline-name"]
        )
        assert (
            nonadmin_client.session[SessionKeyEnum.DATA_INTERFACE.value][
                "data_interface-name"
            ]
            == data["data_interface-name"]
        )
        assert Pipeline.objects.all().count() == 0
        assert DataInterface.objects.all().count() == 0

    def test_post_data_to_edit_pipeline(self, nonadmin_user, nonadmin_client, project):
        CollaboratorFactory(project=project, user=nonadmin_user)
        pipeline = PipelineFactory()
        datainterface = pipeline.input
        StepFactory(pipeline=pipeline)
        data = {
            "pipeline-name": "new pipeline name",
            "data_interface-name": "new data interface name",
            "data_interface-interface_type": "database",
            "data_interface-connection_string": datainterface.connection_string,
        }
        response = nonadmin_client.post(
            reverse("projects:edit_pipeline", args=(project.pk, pipeline.pk)),
            data=data,
        )
        assert response.status_code == HTTPStatus.FOUND.numerator, (
            "Pipeline form errors: "
            + str(response.context["form_pipeline"].errors)
            + "\nData interface form errors: "
            + str(response.context["form_datainterface"].errors)
        )
        # Check session for saved values
        assert (
            nonadmin_client.session[SessionKeyEnum.PIPELINE.value]["pipeline-name"]
            == data["pipeline-name"]
        )
        assert (
            nonadmin_client.session[SessionKeyEnum.DATA_INTERFACE.value][
                "data_interface-name"
            ]
            == data["data_interface-name"]
        )
        # Check that values haven't changed in DB
        db_pipeline = Pipeline.objects.get(pk=pipeline.pk)
        assert pipeline.name == db_pipeline.name
        db_data_interface = DataInterface.objects.get(pk=datainterface.pk)
        assert datainterface.name == db_data_interface.name


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

    def save_step2_data_in_session(self, client, pipeline, datainterface):
        session = client.session
        session[SessionKeyEnum.DATA_INTERFACE.value] = {
            f"{DataInterfaceForm.prefix}-{key}": getattr(datainterface, key)
            for key in DataInterfaceForm._meta.fields
        }
        session[SessionKeyEnum.PIPELINE.value] = {
            f"{PipelineForm.prefix}-{key}": getattr(pipeline, key)
            for key in PipelineForm._meta.fields
        }
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
            "save": "true",
        }

        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)
        assert Pipeline.objects.count() == 0
        assert DataInterface.objects.count() == 0
        assert Step.objects.count() == 0
        assert Pipeline.objects.count() == 0

        response = nonadmin_client.post(
            reverse("projects:new_step", args=(project.pk,)),
            data=data,
        )
        assert (
            response.status_code == HTTPStatus.FOUND.numerator
        ), "Form errors: " + str(response.context["form_step"].errors)
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

    def test_back_new_step_post(self, nonadmin_client, project):
        pipeline = PipelineFactory.build(project=project)
        datainterface = pipeline.input
        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)

        data = {
            "name": "new name",
            "script": "new script",
            "back": "true",
        }

        response = nonadmin_client.post(
            reverse("projects:new_step", args=(project.pk,)),
            data=data,
            follow=True,
        )

        assert response.status_code == HTTPStatus.OK.numerator
        assert Pipeline.objects.count() == 0
        assert DataInterface.objects.count() == 0
        assert Step.objects.count() == 0
        assert (
            nonadmin_client.session[SessionKeyEnum.STEP.value]["name"] == data["name"]
        )
        assert (
            nonadmin_client.session[SessionKeyEnum.STEP.value]["script"]
            == data["script"]
        )

    def test_edit_step_get(self, nonadmin_client, project):
        step_model = StepFactory(pipeline=PipelineFactory(project=project))
        pipeline = step_model.pipeline
        datainterface = pipeline.input
        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)

        data = {
            "name": [pipeline.name, datainterface.name],
            "interface_type": ["database"],
            "connection_string": [datainterface.connection_string],
            "script": step_model.script,
        }
        response = nonadmin_client.post(
            reverse(
                "projects:edit_step",
                kwargs={
                    "project_id": project.id,
                    "step_id": step_model.pk,
                },
            ),
            data=data,
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
        assert (
            response.status_code == HTTPStatus.FOUND.numerator
        ), "Form errors: " + str(response.context["form_step"].errors)
        edited_step_model = Step.objects.get(pk=step_model.pk)
        assert data["name"] == edited_step_model.name
        assert data["script"] == edited_step_model.script

    def test_back_edit_step_post(self, nonadmin_user, nonadmin_client, project):
        step_model = StepFactory(pipeline=PipelineFactory(project=project))
        pipeline = step_model.pipeline
        datainterface = pipeline.input

        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)

        data = {
            "name": "new name",
            "script": "new script",
            "back": "true",
        }

        response = nonadmin_client.post(
            reverse("projects:edit_step", args=(project.pk, step_model.pk)),
            data=data,
            follow=True,
        )

        assert response.status_code == HTTPStatus.OK.numerator
        assert Pipeline.objects.count() == 1
        assert DataInterface.objects.count() == 1
        assert Step.objects.count() == 1
        assert SessionKeyEnum.STEP.value in nonadmin_client.session
        assert (
            nonadmin_client.session[SessionKeyEnum.STEP.value]["name"] == data["name"]
        )
        assert pipeline.name in str(response.content)
