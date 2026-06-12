from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .roles import es_cliente, es_supervisor, es_admin, obtener_rol_usuario


def cliente_requerido(view_func):
    """Decorador que requiere que el usuario tenga rol de Cliente."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not es_cliente(request.user):
            raise PermissionDenied(
                "Se requiere rol de cliente para acceder a este recurso."
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def supervisor_requerido(view_func):
    """Decorador que requiere que el usuario tenga rol de Supervisor."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not es_supervisor(request.user):
            raise PermissionDenied(
                "Se requiere rol de supervisor para acceder a este recurso."
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_requerido(view_func):
    """Decorador que requiere que el usuario sea administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not es_admin(request.user):
            raise PermissionDenied(
                "Se requiere rol de administrador para acceder a este recurso."
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def solo_get_y_head(view_func):
    """Decorador que restringe a métodos HTTP GET y HEAD."""
    @wraps(view_func)
    @require_http_methods(["GET", "HEAD"])
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def solo_post(view_func):
    """Decorador que restringe a método HTTP POST."""
    @wraps(view_func)
    @require_http_methods(["POST"])
    @csrf_protect
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def supervisor_solo_lectura(view_func):
    """
    Decorador que permite a supervisores solo acceso de lectura.
    Rechaza métodos POST, PUT, DELETE.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not es_supervisor(request.user):
            raise PermissionDenied(
                "Se requiere rol de supervisor para acceder a este recurso."
            )
        
        metodos_bloqueados = ['POST', 'PUT', 'DELETE', 'PATCH']
        if request.method in metodos_bloqueados:
            raise PermissionDenied(
                "Los supervisores solo pueden acceder en lectura."
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def proteger_id_usuario(view_func):
    """
    Decorador que protege contra acceso no autorizado a recursos de otros usuarios.
    Comprueba que el 'user_id' en kwargs pertenezca al usuario actual.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_id = kwargs.get('user_id') or kwargs.get('cliente_id')
        
        if user_id and request.user.id != int(user_id):
            # Solo permitir si es supervisor
            if not es_supervisor(request.user):
                raise PermissionDenied(
                    "No tienes permiso para acceder a los recursos de otro usuario."
                )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def proteger_bien_id(view_func):
    """
    Decorador que valida que el bien pertenezca al usuario actual.
    Útil para proteger contra IDOR (Insecure Direct Object Reference).
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        bien_id = kwargs.get('bien_id')
        
        if bien_id and es_cliente(request.user):
            from apps.bienes.models import Bien
            
            try:
                bien = Bien.objects.get(id=bien_id)
                if bien.cliente.usuario != request.user:
                    raise PermissionDenied(
                        "No tienes permiso para acceder a este bien."
                    )
            except Bien.DoesNotExist:
                return HttpResponseBadRequest(
                    "El bien especificado no existe."
                )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def validar_token_api(view_func):
    """
    Decorador que valida un token en el header Authorization.
    Se usa para endpoints de API (ej: servicio GPS).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from django.conf import settings
        
        token = request.headers.get('Authorization', '').replace('Token ', '')
        
        if not token or token != getattr(settings, 'GPS_API_TOKEN', ''):
            return HttpResponseForbidden(
                "Token de autenticación inválido o ausente."
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


class RolRequeridoMixin:
    """Mixin para vistas basadas en clases que requieren un rol específico."""
    rol_requerido = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied(
                "Debes estar autenticado para acceder a este recurso."
            )
        
        if self.rol_requerido == 'cliente' and not es_cliente(request.user):
            raise PermissionDenied(
                "Se requiere rol de cliente."
            )
        
        if self.rol_requerido == 'supervisor' and not es_supervisor(request.user):
            raise PermissionDenied(
                "Se requiere rol de supervisor."
            )
        
        if self.rol_requerido == 'admin' and not es_admin(request.user):
            raise PermissionDenied(
                "Se requiere rol de administrador."
            )
        
        return super().dispatch(request, *args, **kwargs)