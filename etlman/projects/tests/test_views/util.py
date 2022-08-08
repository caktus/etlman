from django.test import Client

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
