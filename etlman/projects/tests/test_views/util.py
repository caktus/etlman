from http import HTTPStatus
from random import randint
from typing import Optional

import pytest
from django.forms import model_to_dict
from django.test import Client
from django.urls import reverse

from etlman.projects.models import Project, Step
from etlman.projects.tests.factories import PipelineFactory, ProjectFactory, StepFactory
from etlman.projects.views import MessagesEnum
from etlman.users.models import User



def get_anon_client():
    return Client()


def get_authenticated_client(username="testuser"):
    client, _ = get_authenticated_client_and_test_user(username)
    return client


def get_authenticated_client_and_test_user(username="testuser"):
    client = get_anon_client()
    user, _ = User.objects.get_or_create(username=username)
    client.force_login(user)
    return client, user
