
from django.http import HttpRequest


def user_is_authenticated(request: HttpRequest, **view_kwargs: dict) -> bool:
    return request.user.is_authenticated 


def user_is_project_collaborator(request: HttpRequest, **view_kwargs: dict) -> bool:
    project_id = view_kwargs["project_id"]
    return request.user.is_authenticated and request.user.projects.filter(pk=project_id).exists()
