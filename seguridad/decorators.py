# seguridad/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from .roles import es_cliente


def cliente_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not es_cliente(request.user):
            raise PermissionDenied("Se requiere rol de cliente.")

        return view_func(request, *args, **kwargs)

    return wrapper

def supervisor_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not es_supervisor(request.user):
            raise PermissionDenied("Se requiere rol de supervisor.")

        return view_func(request, *args, **kwargs)

    return wrapper