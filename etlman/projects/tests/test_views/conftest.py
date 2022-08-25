import pytest
from django.test.client import Client

from etlman.projects.models import Project, User
from etlman.projects.tests.factories import CollaboratorFactory, ProjectFactory


# Adapted from pytest 'admin_user' and 'admin_client':
# https://github.com/pytest-dev/pytest-django/blob/fba51531f067a985ec6b6be4aec9a2ed5766d69c/pytest_django/fixtures.py#L406-L447
@pytest.fixture()
def nonadmin_user(
    db: None,
    django_user_model,
    django_username_field: str,
) -> User:
    """A Django test user.
    This uses an existing user with username "testuser", or creates a new one with
    password "password".
    """
    UserModel = django_user_model
    username_field = django_username_field
    username = "testuser@example.com" if username_field == "email" else "testuser"

    try:
        # The default behavior of `get_by_natural_key()` is to look up by `username_field`.
        # However the user model is free to override it with any sort of custom behavior.
        # The Django authentication backend already assumes the lookup is by username,
        # so we can assume so as well.
        user = UserModel._default_manager.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        user_data = {}
        if "email" in UserModel.REQUIRED_FIELDS:
            user_data["email"] = "testuser@example.com"
        user_data["password"] = "password"
        user_data[username_field] = username
        user = UserModel._default_manager.create_user(**user_data)
    return user


@pytest.fixture()
def nonadmin_client(
    db: None,
    nonadmin_user,
) -> Client:
    """A Django test client logged in as an non-admin user."""

    client = Client()
    client.force_login(nonadmin_user)
    return client


@pytest.fixture()
def project(nonadmin_user, nonadmin_client) -> Project:
    """A project"""

    project = ProjectFactory()
    CollaboratorFactory(project=project, user=nonadmin_user)
    return project
