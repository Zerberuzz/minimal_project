# seguridad/roles.py

GRUPO_CLIENTE = "cliente"
GRUPO_SUPERVISOR = "supervisor"
def pertenece_a_grupo(user, nombre_grupo):
    return user.is_authenticated and user.groups.filter(name=nombre_grupo).exists()


def es_cliente(user):
    return pertenece_a_grupo(user, GRUPO_CLIENTE)


def es_supervisor(user):
    return pertenece_a_grupo(user, GRUPO_SUPERVISOR)


