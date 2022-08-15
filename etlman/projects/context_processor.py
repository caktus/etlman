from etlman.projects.models import Project


def current_user_projects(request):
    """
    Filters all projects and returns those that belong
    to the current user.
    """
    username = request.user
    return {
        "current_user_projects": Project.objects.all().filter(
            collaborators=username.id
        ),
    }
