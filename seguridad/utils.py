import logging
from django.utils import timezone
from seguridad.models import Bitacora


logger = logging.getLogger('django.security')


def obtener_ip_cliente(request):
    """Obtiene la IP real del cliente considerando proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def registrar_en_bitacora(
    usuario=None,
    rol='anonimo',
    accion='',
    resultado='exitoso',
    descripcion='',
    request=None,
    datos_adicionales=None
):
    """
    Registra una acción en la bitácora para auditoría y no repudio.
    
    Args:
        usuario: Usuario que realiza la acción (User instance o None)
        rol: Rol del usuario (string)
        accion: Tipo de acción (debe estar en las opciones del modelo)
        resultado: 'exitoso', 'rechazado' o 'error'
        descripcion: Descripción detallada de la acción
        request: HttpRequest object para obtener IP, método HTTP, etc.
        datos_adicionales: Dict con información adicional para auditoría
    """
    
    if not request:
        return None
    
    try:
        bitacora = Bitacora.objects.create(
            usuario=usuario,
            rol=rol,
            accion=accion,
            resultado=resultado,
            descripcion=descripcion,
            ip_origen=obtener_ip_cliente(request),
            metodo_http=request.method,
            ruta=request.path,
            datos_adicionales=datos_adicionales or {}
        )
        
        logger.info(
            f"Bitácora: {usuario or 'anónimo'} - {accion} - {resultado}"
        )
        
        return bitacora
        
    except Exception as e:
        logger.error(f"Error registrando en bitácora: {str(e)}")
        return None


def registrar_login_exitoso(usuario, request):
    """Registra un login exitoso."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='cliente' if hasattr(usuario, 'cliente') else 'administrador',
        accion='login',
        resultado='exitoso',
        descripcion=f'Usuario {usuario.username} inició sesión exitosamente',
        request=request,
        datos_adicionales={
            'username': usuario.username,
            'email': usuario.email,
        }
    )


def registrar_login_fallido(username, request):
    """Registra un intento fallido de login."""
    registrar_en_bitacora(
        usuario=None,
        rol='anonimo',
        accion='login_fallido',
        resultado='rechazado',
        descripcion=f'Intento de login fallido con usuario: {username}',
        request=request,
        datos_adicionales={
            'username': username,
        }
    )


def marcar_bitacora_acceso_denegado(request):
    if request is not None:
        setattr(request, '_bitacora_acceso_denegado', True)


def _rol_de_usuario(usuario):
    if not usuario:
        return 'anonimo'
    grupos = usuario.groups.all()
    return grupos[0].name if grupos else 'usuario'


def registrar_acceso_no_autorizado(usuario, accion, descripcion, request):
    """Registra un intento de acceso no autorizado."""
    registrar_en_bitacora(
        usuario=usuario,
        rol=_rol_de_usuario(usuario),
        accion='acceso_no_autorizado',
        resultado='rechazado',
        descripcion=descripcion,
        request=request,
        datos_adicionales={
            'accion_intentada': accion,
        }
    )
    marcar_bitacora_acceso_denegado(request)


def registrar_acceso_denegado(usuario, accion_intentada, descripcion, request):
    """Registra un evento de acceso denegado (403 Forbidden)."""
    registrar_en_bitacora(
        usuario=usuario,
        rol=_rol_de_usuario(usuario),
        accion='acceso_denegado',
        resultado='rechazado',
        descripcion=descripcion,
        request=request,
        datos_adicionales={
            'accion_intentada': accion_intentada,
        }
    )
    marcar_bitacora_acceso_denegado(request)


def registrar_alta_cliente_exitoso(usuario, request):
    """Registra cuando un nuevo cliente se da de alta correctamente."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='cliente',
        accion='alta_cliente',
        resultado='exitoso',
        descripcion=f'Cliente registrado exitosamente: {usuario.username}',
        request=request,
        datos_adicionales={
            'username': usuario.username,
            'email': usuario.email,
        }
    )


def registrar_alta_cliente_rechazada(username, motivo, request):
    """Registra un intento rechazado de alta de cliente."""
    registrar_en_bitacora(
        usuario=None,
        rol='anonimo',
        accion='alta_cliente',
        resultado='rechazado',
        descripcion=f'Intento rechazado de alta de cliente: {motivo}',
        request=request,
        datos_adicionales={
            'username': username,
            'motivo': motivo,
        }
    )


def registrar_creacion_bien(usuario, bien_id, request):
    """Registra la creación de un bien."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='cliente',
        accion='crear_bien',
        resultado='exitoso',
        descripcion=f'Bien creado: {bien_id}',
        request=request,
        datos_adicionales={
            'bien_id': bien_id,
        }
    )


def registrar_actualizacion_bien(usuario, bien_id, cambios, request):
    """Registra la actualización de un bien."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='cliente',
        accion='actualizar_bien',
        resultado='exitoso',
        descripcion=f'Bien actualizado: {bien_id}',
        request=request,
        datos_adicionales={
            'bien_id': bien_id,
            'cambios': cambios,
        }
    )

def registrar_eliminacion_bien(usuario, bien_id, request):
    """Registra la eliminación de un bien."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='cliente',
        accion='eliminar_bien',
        resultado='exitoso',
        descripcion=f'Bien eliminado: {bien_id}',
        request=request,
        datos_adicionales={
            'bien_id': bien_id,
        }
    )

def registrar_creacion_direccion(usuario, direccion_id, request):
    """Registra la creación de una dirección."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='cliente',
        accion='crear_direccion',
        resultado='exitoso',
        descripcion=f'Dirección creada con ID: {direccion_id}',
        request=request,
        datos_adicionales={
            'direccion_id': direccion_id,
        }
    )


def registrar_consulta_reporte(usuario, tipo_reporte, request):
    """Registra la consulta de reportes."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='supervisor' if hasattr(usuario, 'groups') else 'cliente',
        accion='consultar_reporte',
        resultado='exitoso',
        descripcion=f'Reporte consultado: {tipo_reporte}',
        request=request,
        datos_adicionales={
            'tipo_reporte': tipo_reporte,
        }
    )


def registrar_consulta_bitacora(usuario, filtros, request):
    """Registra la consulta de la bitácora."""
    registrar_en_bitacora(
        usuario=usuario,
        rol='supervisor',
        accion='consultar_bitacora',
        resultado='exitoso',
        descripcion='Bitácora consultada',
        request=request,
        datos_adicionales={
            'filtros': filtros,
        }
    )


def registrar_gps_valida(camion_id, latitud, longitud, request):
    """Registra una actualización GPS válida."""
    registrar_en_bitacora(
        usuario=None,
        rol='anonimo',
        accion='actualizar_gps',
        resultado='exitoso',
        descripcion=f'Actualización GPS válida para camión {camion_id}',
        request=request,
        datos_adicionales={
            'camion_id': camion_id,
            'latitud': str(latitud),
            'longitud': str(longitud),
        }
    )


def registrar_gps_rechazada(camion_id, motivo, request):
    """Registra una actualización GPS rechazada."""
    registrar_en_bitacora(
        usuario=None,
        rol='anonimo',
        accion='actualizar_gps',
        resultado='rechazado',
        descripcion=f'Actualización GPS rechazada: {motivo}',
        request=request,
        datos_adicionales={
            'camion_id': camion_id,
            'motivo': motivo,
        }
    )
