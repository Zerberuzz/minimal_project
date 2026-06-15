from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin

from seguridad.utils import registrar_acceso_denegado


class Bitacora403Middleware(MiddlewareMixin):
    """Middleware para registrar accesos denegados y recursos no autorizados."""

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            if getattr(request, '_bitacora_acceso_denegado', False):
                return None

            descripcion = f'Acceso denegado: {str(exception)}'
            usuario = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            registrar_acceso_denegado(
                usuario,
                accion_intentada='permission_denied',
                descripcion=descripcion,
                request=request
            )
        return None

    def process_response(self, request, response):
        if response.status_code == 403 and not getattr(request, '_bitacora_acceso_denegado', False):
            descripcion = 'Acceso denegado a recurso no autorizado.'
            usuario = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            registrar_acceso_denegado(
                usuario,
                accion_intentada='forbidden_response',
                descripcion=descripcion,
                request=request
            )
        return response
