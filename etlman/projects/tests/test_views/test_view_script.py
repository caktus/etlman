from http import HTTPStatus

import pytest
from django.urls import reverse

from etlman.projects.tests.factories import CollaboratorFactory, PipelineFactory


@pytest.mark.django_db
class TestHTMLInViews:
    def test_pipeline_authorizer(self, nonadmin_client):
        pipeline = PipelineFactory()
        response = nonadmin_client.get(
            reverse("projects:list_pipeline", args=(pipeline.project.pk,)), follow=True
        )
        assert response.status_code == HTTPStatus.FORBIDDEN.numerator

    def test_pipeline_table_headers_and_tags_in_html(
        self, nonadmin_user, nonadmin_client
    ):
        pipeline = PipelineFactory()
        CollaboratorFactory(project=pipeline.project, user=nonadmin_user)
        response = nonadmin_client.get(
            reverse("projects:list_pipeline", args=(pipeline.project.pk,)), follow=True
        )
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert "Name" in html
        assert "Actions" in html
        assert "<thead>" in html
        assert "<table" in html
        assert "Add Pipeline" in html

    def test_pipeline_table_content_in_html_one_pipeline(
        self, nonadmin_user, nonadmin_client
    ):
        pipeline = PipelineFactory()
        CollaboratorFactory(project=pipeline.project, user=nonadmin_user)
        response = nonadmin_client.get(
            reverse("projects:list_pipeline", args=(pipeline.project.pk,)), follow=True
        )
        context = response.context

        assert response.status_code == HTTPStatus.OK.numerator
        assert pipeline in context["pipeline_list"]

    def test_pipeline_table_content_in_html_no_input(
        self, nonadmin_user, nonadmin_client
    ):
        pipeline = PipelineFactory(input=None)
        CollaboratorFactory(project=pipeline.project, user=nonadmin_user)
        no_data_interface_msg = "No data interface attached"
        response = nonadmin_client.get(
            reverse("projects:list_pipeline", args=(pipeline.project.pk,)), follow=True
        )
        html = str(response.content)

        assert response.status_code == HTTPStatus.OK.numerator
        assert pipeline.name in html
        assert no_data_interface_msg in html
