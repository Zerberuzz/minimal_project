import re
from datetime import date

from django.core.exceptions import ValidationError

PATRON_ID_BIEN = re.compile(r"^b-\d{4}-\d{4}$")


def validar_identificador_bien(valor):
    if not PATRON_ID_BIEN.match(valor):
        raise ValidationError(
            "El identificador debe tener el formato b-XXXX-año."
        )

    anio = int(valor.split("-")[2])
    anio_actual = date.today().year

    if anio < 2000 or anio > anio_actual:
        raise ValidationError(
            f"El año debe estar entre 2000 y {anio_actual}."
        )