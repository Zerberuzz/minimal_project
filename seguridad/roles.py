from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied

GRUPO_CLIENTE = "cliente"
GRUPO_SUPERVISOR = "supervisor"


def crear_grupos_si_no_existen():
    """Crea los grupos Cliente y Supervisor si no existen."""
    Group.objects.get_or_create(name=GRUPO_CLIENTE)
    Group.objects.get_or_create(name=GRUPO_SUPERVISOR)


def pertenece_a_grupo(user, nombre_grupo):
    """Verifica si un usuario pertenece a un grupo específico."""
    if not user or not user.is_authenticated:
        return False
    
    return user.groups.filter(name=nombre_grupo).exists()


def es_cliente(user):
    """Verifica si el usuario tiene rol de Cliente."""
    return pertenece_a_grupo(user, GRUPO_CLIENTE)


def es_supervisor(user):
    """Verifica si el usuario tiene rol de Supervisor."""
    return pertenece_a_grupo(user, GRUPO_SUPERVISOR)


def es_admin(user):
    """Verifica si el usuario es administrador del sistema."""
    if not user or not user.is_authenticated:
        return False
    
    return user.is_staff or user.is_superuser


def obtener_rol_usuario(user):
    """Retorna el rol del usuario como string."""
    if not user or not user.is_authenticated:
        return "anonimo"
    
    if es_admin(user):
        return "administrador"
    
    if es_supervisor(user):
        return "supervisor"
    
    if es_cliente(user):
        return "cliente"
    
    return "usuario"


def asignar_rol_cliente(user):
    """Asigna el rol de Cliente a un usuario."""
    crear_grupos_si_no_existen()
    grupo_cliente = Group.objects.get(name=GRUPO_CLIENTE)
    user.groups.add(grupo_cliente)
    
    # Remover otros roles
    grupo_supervisor = Group.objects.get(name=GRUPO_SUPERVISOR)
    user.groups.remove(grupo_supervisor)


def asignar_rol_supervisor(user):
    """Asigna el rol de Supervisor a un usuario."""
    crear_grupos_si_no_existen()
    grupo_supervisor = Group.objects.get(name=GRUPO_SUPERVISOR)
    user.groups.add(grupo_supervisor)
    
    # Remover otros roles
    grupo_cliente = Group.objects.get(name=GRUPO_CLIENTE)
    user.groups.remove(grupo_cliente)


def remover_rol(user, nombre_grupo):
    """Remueve un rol específico de un usuario."""
    try:
        grupo = Group.objects.get(name=nombre_grupo)
        user.groups.remove(grupo)
    except Group.DoesNotExist:
        pass