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
    return token == settings.TOKEN_RASTREO_CAMIONES
