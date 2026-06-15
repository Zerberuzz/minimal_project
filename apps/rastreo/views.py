import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from seguridad.tokens import obtener_token_bearer, token_valido
from seguridad.validaciones import (
    validar_fecha_hora,
    validar_latitud,
    validar_longitud,
    validar_velocidad,
)
from seguridad.utils import registrar_gps_valida, registrar_gps_rechazada
from .models import UbicacionCamion

@csrf_exempt
@require_POST
def registrar_ubicacion(request):
    token = obtener_token_bearer(request)
    if token is None or not token_valido(token):
        registrar_gps_rechazada('desconocido', 'Token inválido o ausente', request)
        return JsonResponse(
            {"error": "Token inválido o ausente."},
            status=401
        )
    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        registrar_gps_rechazada('desconocido', 'El cuerpo debe ser JSON válido', request)
        return JsonResponse(
            {"error": "El cuerpo debe ser JSON válido."},
            status=400
        )
    
    camion_id = datos.get("camion_id")
    if not camion_id:
        registrar_gps_rechazada('desconocido', 'El campo camion_id es obligatorio', request)
        return JsonResponse(
            {"error": "El campo camion_id es obligatorio."},
            status=400
        )
    
    try:
        latitud = validar_latitud(datos.get("latitud"))
        longitud = validar_longitud(datos.get("longitud"))
        velocidad = validar_velocidad(datos.get("velocidad"))
        registrado_en = validar_fecha_hora(datos.get("registrado_en"))
    except ValueError as error:
        registrar_gps_rechazada(camion_id, str(error), request)
        return JsonResponse(
            {"error": str(error)},
            status=400
        )
    
    ubicacion = UbicacionCamion.objects.create(
        camion_id=camion_id,
        latitud=latitud,
        longitud=longitud,
        velocidad=velocidad,
        registrado_en=registrado_en
    )
    
    registrar_gps_valida(camion_id, latitud, longitud, request)
    
    return JsonResponse(
        {
            "mensaje": "Ubicación registrada correctamente.",
            "ubicacion_id": ubicacion.id
        },
        status=201
    )
