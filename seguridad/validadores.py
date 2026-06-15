import re
import html
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.core.exceptions import ValidationError


# Patrones de validación
PATRON_ID_BIEN = re.compile(r"^b-\d{4}-\d{4}$")
PATRON_TELEFONO = re.compile(r"^\+?1?\d{9,15}$")
PATRON_EMAIL = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


# ============================================================================
# VALIDADORES DE DESCRIPCIÓN (Bien)
# ============================================================================

def validar_descripcion_bien(valor):
    """
    Valida la descripción del bien:
    - Obligatoria
    - Longitud máxima 500 caracteres
    - Sanitización: Eliminar espacios al inicio/final y escapar HTML
    """
    if not valor:
        raise ValidationError("La descripción del bien es obligatoria.")
    
    valor = valor.strip()
    
    if len(valor) > 500:
        raise ValidationError("La descripción no puede exceder 500 caracteres.")
    
    if len(valor) < 5:
        raise ValidationError("La descripción debe tener al menos 5 caracteres.")
    
    # Validar que no contenga caracteres peligrosos sin escapar
    caracteres_peligrosos = ['<', '>', '"', "'", '&']
    for char in caracteres_peligrosos:
        if char in valor and not (char == '&' and '&amp;' in valor):
            raise ValidationError(
                "La descripción contiene caracteres no permitidos. "
                "Se escaparán automáticamente al guardar."
            )
    
    return valor


def sanitizar_descripcion(valor):
    """Sanitiza la descripción escapando caracteres HTML."""
    if not valor:
        return ""
    valor = valor.strip()
    return html.escape(valor)


# ============================================================================
# VALIDADORES DE VALOR (Bien)
# ============================================================================

def validar_valor_bien(valor):
    """
    Valida el valor del bien:
    - Numérico (Decimal)
    - Estrictamente mayor que cero
    - Máximo 2 decimales
    """
    if valor is None or valor == "":
        raise ValidationError("El valor del bien es obligatorio.")
    
    try:
        valor_decimal = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(
            "El valor debe ser un número válido (ej: 1500.00)."
        )
    
    if valor_decimal <= 0:
        raise ValidationError("El valor del bien debe ser mayor a cero.")
    
    if valor_decimal > Decimal('999999999.99'):
        raise ValidationError("El valor excede el límite máximo permitido.")
    
    return valor_decimal


# ============================================================================
# VALIDADORES DE ESTATUS (Bien)
# ============================================================================

def validar_estatus_bien(valor):
    """
    Valida el estatus del bien:
    - Debe estar en la lista cerrada de valores permitidos
    """
    estatus_permitidos = ['Registrado', 'En tránsito', 'Entregado']
    
    if not valor:
        raise ValidationError("El estatus del bien es obligatorio.")
    
    if valor not in estatus_permitidos:
        raise ValidationError(
            f"El estatus debe ser uno de: {', '.join(estatus_permitidos)}."
        )
    
    return valor


# ============================================================================
# VALIDADORES DE DIRECCIONES (Recolección y Entrega)
# ============================================================================

def validar_calle(valor):
    """Valida el nombre de la calle."""
    if not valor:
        raise ValidationError("La calle es obligatoria.")
    
    valor = valor.strip()
    
    if len(valor) < 3:
        raise ValidationError("La calle debe tener al menos 3 caracteres.")
    
    if len(valor) > 150:
        raise ValidationError("La calle no puede exceder 150 caracteres.")
    
    return sanitizar_texto(valor)


def validar_numero_exterior(valor):
    """Valida el número exterior."""
    if not valor:
        raise ValidationError("El número exterior es obligatorio.")
    
    valor = valor.strip()
    
    if len(valor) > 20:
        raise ValidationError("El número exterior no puede exceder 20 caracteres.")
    
    return valor


def validar_numero_interior(valor):
    """Valida el número interior (opcional)."""
    if valor:
        valor = valor.strip()
        if len(valor) > 20:
            raise ValidationError(
                "El número interior no puede exceder 20 caracteres."
            )
        return valor
    return ""


def validar_ciudad(valor):
    """Valida la ciudad."""
    if not valor:
        raise ValidationError("La ciudad es obligatoria.")
    
    valor = valor.strip()
    
    if len(valor) < 3:
        raise ValidationError("La ciudad debe tener al menos 3 caracteres.")
    
    if len(valor) > 100:
        raise ValidationError("La ciudad no puede exceder 100 caracteres.")
    
    return sanitizar_texto(valor)


def validar_codigo_postal(valor):
    """Valida el código postal."""
    if not valor:
        raise ValidationError("El código postal es obligatorio.")
    
    valor = valor.strip()
    
    # Patrón para códigos postales mexicanos (XXXXX o XXXXX-XXXX)
    patron_cp = re.compile(r"^\d{5}(-\d{4})?$")
    
    if not patron_cp.match(valor):
        raise ValidationError(
            "El código postal debe tener el formato XXXXX o XXXXX-XXXX."
        )
    
    return valor


def validar_estado(valor):
    """Valida el estado/provincia."""
    if not valor:
        raise ValidationError("El estado es obligatorio.")
    
    valor = valor.strip()
    
    if len(valor) < 3:
        raise ValidationError("El estado debe tener al menos 3 caracteres.")
    
    if len(valor) > 100:
        raise ValidationError("El estado no puede exceder 100 caracteres.")
    
    return sanitizar_texto(valor)


def sanitizar_texto(valor):
    """Sanitiza texto normalizando espacios y escapando HTML."""
    if not valor:
        return ""
    
    # Normalizar espacios múltiples
    valor = ' '.join(valor.split())
    valor = valor.strip()
    
    return html.escape(valor)


# ============================================================================
# VALIDADORES DE COORDENADAS GPS
# ============================================================================

def validar_latitud(valor):
    """
    Valida la latitud:
    - Numérico (decimal)
    - Entre -90 y 90
    - Hasta 6 decimales
    """
    if valor is None or valor == "":
        raise ValidationError("La latitud es obligatoria.")
    
    try:
        latitud = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("La latitud debe ser un número válido.")
    
    if latitud < Decimal("-90") or latitud > Decimal("90"):
        raise ValidationError(
            "La latitud debe estar entre -90 y 90 grados."
        )
    
    try:
        return latitud.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValidationError("La latitud debe tener hasta 6 decimales.")


def validar_longitud(valor):
    """
    Valida la longitud:
    - Numérico (decimal)
    - Entre -180 y 180
    - Hasta 6 decimales
    """
    if valor is None or valor == "":
        raise ValidationError("La longitud es obligatoria.")
    
    try:
        longitud = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("La longitud debe ser un número válido.")
    
    if longitud < Decimal("-180") or longitud > Decimal("180"):
        raise ValidationError(
            "La longitud debe estar entre -180 y 180 grados."
        )
    
    try:
        return longitud.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValidationError("La longitud debe tener hasta 6 decimales.")


# ============================================================================
# VALIDADOR DE IDENTIFICADOR DE BIEN
# ============================================================================

def validar_identificador_bien(valor):
    """
    Valida el identificador del bien:
    - Formato: b-XXXX-YYYY donde YYYY es el año
    - El año debe estar entre 2000 y el año actual
    """
    if not valor:
        raise ValidationError("El identificador del bien es obligatorio.")
    
    valor = valor.strip().lower()
    
    if not PATRON_ID_BIEN.match(valor):
        raise ValidationError(
            "El identificador debe tener el formato b-XXXX-YYYY (ej: b-0001-2024)."
        )
    
    partes = valor.split("-")
    anio = int(partes[2])
    anio_actual = date.today().year
    
    if anio < 2000 or anio > anio_actual:
        raise ValidationError(
            f"El año debe estar entre 2000 y {anio_actual}."
        )
    
    return valor


# ============================================================================
# VALIDADOR DE IDENTIFICADOR DE CLIENTE
# ============================================================================

def validar_identificador_cliente(valor):
    """
    Valida el identificador del cliente:
    - Alfanumérico
    - Longitud entre 5 y 30 caracteres
    """
    if not valor:
        raise ValidationError("El identificador del cliente es obligatorio.")
    
    valor = valor.strip()
    
    if not re.match(r"^[a-zA-Z0-9_]{5,30}$", valor):
        raise ValidationError(
            "El identificador debe contener solo letras, números, guiones y guiones bajos, "
            "con una longitud entre 5 y 30 caracteres."
        )
    
    return valor


# ============================================================================
# VALIDADORES DE INFORMACIÓN PERSONAL
# ============================================================================

def validar_nombre(valor):
    """Valida un nombre (nombre, apellido)."""
    if not valor:
        raise ValidationError("El nombre es obligatorio.")
    
    valor = valor.strip()
    
    if len(valor) < 2:
        raise ValidationError("El nombre debe tener al menos 2 caracteres.")
    
    if len(valor) > 120:
        raise ValidationError("El nombre no puede exceder 120 caracteres.")
    
    # Solo letras, espacios y algunos caracteres permitidos
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s'-]{2,}$", valor):
        raise ValidationError(
            "El nombre contiene caracteres no permitidos."
        )
    
    return sanitizar_texto(valor)


def validar_email(valor):
    """Valida el correo electrónico."""
    if not valor:
        raise ValidationError("El correo electrónico es obligatorio.")
    
    valor = valor.strip().lower()
    
    if not PATRON_EMAIL.match(valor):
        raise ValidationError("El formato del correo electrónico no es válido.")
    
    if len(valor) > 254:
        raise ValidationError("El correo electrónico es demasiado largo.")
    
    return valor


def validar_telefono(valor):
    """Valida el número de teléfono."""
    if not valor:
        raise ValidationError("El teléfono es obligatorio.")
    
    valor = valor.strip()
    
    if not PATRON_TELEFONO.match(valor):
        raise ValidationError(
            "El teléfono debe contener entre 9 y 15 dígitos."
        )
    
    return valor


# ============================================================================
# VALIDADOR DE IDENTIFICADOR DE CAMIÓN
# ============================================================================

def validar_identificador_camion(valor):
    """
    Valida el identificador del camión:
    - Alfanumérico
    - Longitud entre 3 y 20 caracteres
    """
    if not valor:
        raise ValidationError("El identificador del camión es obligatorio.")
    
    valor = valor.strip().upper()
    
    if not re.match(r"^[A-Z0-9_-]{3,20}$", valor):
        raise ValidationError(
            "El identificador del camión debe contener solo letras mayúsculas, "
            "números, guiones y guiones bajos, con longitud entre 3 y 20 caracteres."
        )
    
    return valor


# ============================================================================
# FUNCIÓN GENERAL DE SANITIZACIÓN
# ============================================================================

def sanitizar_entrada_general(valor, max_length=500):
    """
    Sanitización general para inputs de texto:
    - Elimina espacios al inicio/final
    - Escapa HTML
    - Limita longitud
    """
    if not valor:
        return ""
    
    valor = str(valor).strip()
    
    if len(valor) > max_length:
        valor = valor[:max_length]
    
    return html.escape(valor)