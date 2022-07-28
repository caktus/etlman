from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from etlman.projects.forms import StepForm
from etlman.projects.tests.factories import StepFactory, PipelineFactory


@pytest.mark.django_db
class TestEditScriptViewAndForm:

    client = Client()

    def test_edit_script_view_status_code(self):
        response = self.client.get(reverse("projects:step_form_upsert"))
        assert response.status_code == HTTPStatus.OK.numerator
    
    # Add tests for:
    # - GET for existing object - 200 status code, content of script appears in HTML
    # - POST with invalid data - error appears in HTML
    # - POST for new object with valid data returns redirect, saved to DB
    # - POST for existing object with valid data returns redirect, updates saved to DB
