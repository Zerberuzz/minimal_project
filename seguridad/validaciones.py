from decimal import Decimal, InvalidOperation
from django.utils.dateparse import parse_datetime

def convertir_decimal(valor, nombre_campo):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError):
        raise ValueError(f"El campo {nombre_campo} debe ser numérico.")

def validar_latitud(valor):
    latitud = convertir_decimal(valor, "latitud")
    if latitud < -90 or latitud > 90:
        raise ValueError("La latitud debe estar entre -90 y 90.")
    return latitud

def validar_longitud(valor):
    longitud = convertir_decimal(valor, "longitud")
    if longitud < -180 or longitud > 180:
        raise ValueError("La longitud debe estar entre -180 y 180.")
    return longitud

def validar_velocidad(valor):
    velocidad = convertir_decimal(valor, "velocidad")
    if velocidad < 0:
        raise ValueError("La velocidad no puede ser negativa.")
    return velocidad

def validar_fecha_hora(valor):
    fecha = parse_datetime(str(valor))
    if fecha is None:
        raise ValueError(
            "El campo registrado_en debe tener formato ISO 8601."
        )
    return fecha
