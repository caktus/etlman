import os
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
            "data_interface-sql_query": datainterface.sql_query,
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
            "data_interface-sql_query": "new-sql-query.com",
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
class TestDbConnectionTestView:

    connection_string = os.getenv("DATABASE_URL").replace("postgres", "postgresql", 1)

    def test_post_only_view(self, nonadmin_client, project):
        "The view returns an HTTP 405 (method not allowed) when given a GET request."

        response = nonadmin_client.get(
            reverse("projects:test_connection", args=(project.pk,))
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED.numerator

    def test_blank_form_post_data_renders_errors(self, nonadmin_client, project):
        """
        When given an empty field in the POST data, the 'form' variable
        in the context includes the applicable errors.
        """
        data = {
            "data_interface-name": "sample_name",
            "data_interface-interface_type": "database",
            # "data_interface-connection_string": # purposefully empty
            # "data_interface-sql_query":  # purposefully empty
        }

        response = nonadmin_client.post(
            reverse("projects:test_connection", args=(project.pk,)),
            data=data,
        )
        err_msg = {
            "connection_string": ["This field is required."],
            "sql_query": ["This field is required."],
        }
        assert err_msg == response.context["form"].errors

    def test_invalid_db_name_error(self, nonadmin_client, project):
        """
        An otherwise valid DATABASE_URL with a non-existent table includes
        the applicable error message in response.context["message"].
        """
        non_db_name = "etlman_non_existent_db"
        sql_query = "SELECT table_name, FROM INFORMATION_SCHEMA.COLUMNS"
        connection_string = "/".join(
            [self.connection_string.rsplit("/", 1)[0], "etlman_non_existent_db"]
        )
        data = {
            "data_interface-name": "sample_name",
            "data_interface-interface_type": "database",
            "data_interface-connection_string": connection_string,
            "data_interface-sql_query": sql_query,
        }
        response = nonadmin_client.post(
            reverse("projects:test_connection", args=(project.pk,)),
            data=data,
        )
        err_msg = f'database "{non_db_name}" does not exist'
        assert err_msg in response.context["message"]

    def test_invalid_sql_query(self, nonadmin_client, project):
        """
        A valid DATABASE_URL with an invalid SQL query includes the applicable
        error message in response.context["message"].
        """
        sql_query = "invalid SQL query"

        data = {
            "data_interface-name": "sample_name",
            "data_interface-interface_type": "database",
            "data_interface-connection_string": self.connection_string,
            "data_interface-sql_query": sql_query,
        }

        response = nonadmin_client.post(
            reverse("projects:test_connection", args=(project.pk,)),
            data=data,
        )
        err_msg = "[SQL: invalid SQL query]"
        assert err_msg in response.context["message"]

    def test_successful_query(self, nonadmin_client, project):
        """
        A valid connection string and query includes the correct data_columns
        and data_table in response.context.
        """
        sql_query = (
            "SELECT table_name, data_type, table_schema FROM INFORMATION_SCHEMA.COLUMNS"
        )

        data = {
            "data_interface-name": "sample_name",
            "data_interface-interface_type": "database",
            "data_interface-connection_string": self.connection_string,
            "data_interface-sql_query": sql_query,
        }

        response = nonadmin_client.post(
            reverse("projects:test_connection", args=(project.pk,)),
            data=data,
        )
        err_msg = "Database connection successful!"
        assert err_msg in response.context["message"]


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

    def assert_session_cleared(self, client):
        assert SessionKeyEnum.DATA_INTERFACE.value not in client.session
        assert SessionKeyEnum.PIPELINE.value not in client.session

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
            "language": step.language,
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
        self.assert_session_cleared(nonadmin_client)

    def test_back_new_step_post(self, nonadmin_client, project):
        pipeline = PipelineFactory.build(project=project)
        datainterface = pipeline.input
        self.save_step2_data_in_session(nonadmin_client, pipeline, datainterface)

        data = {
            "name": "new name",
            "language": "Python",
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
        response = nonadmin_client.get(
            reverse(
                "projects:edit_step",
                kwargs={
                    "project_id": project.id,
                    "step_id": step_model.pk,
                },
            )
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
            "language": "r",
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
        self.assert_session_cleared(nonadmin_client)

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
