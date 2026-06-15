from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.utils.dateparse import parse_datetime


def convertir_decimal(valor, nombre_campo):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError):
        raise ValueError(f"El campo {nombre_campo} debe ser numérico.")


def validar_latitud(valor):
    latitud = convertir_decimal(valor, "latitud")
    if latitud < Decimal("-90") or latitud > Decimal("90"):
        raise ValueError("La latitud debe estar entre -90 y 90.")
    try:
        return latitud.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError("La latitud debe tener hasta 6 decimales.")


def validar_longitud(valor):
    longitud = convertir_decimal(valor, "longitud")
    if longitud < Decimal("-180") or longitud > Decimal("180"):
        raise ValueError("La longitud debe estar entre -180 y 180.")
    try:
        return longitud.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError("La longitud debe tener hasta 6 decimales.")
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
