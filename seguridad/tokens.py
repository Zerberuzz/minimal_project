from django.conf import settings


def obtener_token_bearer(request):
    encabezado = request.headers.get("Authorization", "")
    if not encabezado.startswith("Bearer "):
        return None
    token = encabezado.replace("Bearer ", "", 1).strip()
    if not token:
        return None
    return token


def token_valido(token):
    """Return True if token matches configured token.

    Uses TOKEN_RASTREO_CAMIONES if present, otherwise falls back to GPS_API_TOKEN.
    This avoids a server-side AttributeError when the first setting is missing.
    """
    expected = getattr(settings, 'TOKEN_RASTREO_CAMIONES', None)
    if expected is None:
        expected = getattr(settings, 'GPS_API_TOKEN', None)
    return expected is not None and token == expected
