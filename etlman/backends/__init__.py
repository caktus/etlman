from django.conf import settings


def get_backend():
    if settings.ETLMAN_BACKEND == "subprocess":
        from .subprocess_backend import SubprocessBackend

        return SubprocessBackend()
    raise ValueError(f"ETLMAN_BACKEND {settings.ETLMAN_BACKEND} is not supported.")
