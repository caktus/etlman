from denied.decorators import allow
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

urlpatterns = [
    path("", allow(TemplateView.as_view(template_name="pages/home.html")), name="home"),
    path(
        "about/",
        allow(TemplateView.as_view(template_name="pages/about.html")),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, allow(admin.site.urls)),
    # User management
    # TODO: Remove allow() below and convert users app to use authorize() decorator
    path("users/", allow(include("etlman.users.urls", namespace="users"))),
    path("projects/", include("etlman.projects.urls", namespace="projects")),
    path("accounts/", allow(include("allauth.urls"))),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            allow(default_views.bad_request),
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            allow(default_views.permission_denied),
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            allow(default_views.page_not_found),
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", allow(default_views.server_error)),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", allow(include(debug_toolbar.urls)))
        ] + urlpatterns
