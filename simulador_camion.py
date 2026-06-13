# simulador_camion.py
import requests
url = "http://127.0.0.1:8000/api/camiones/ubicacion/"
headers = {
"Content-Type": "application/json",
"Authorization": "Bearer TOKEN_DE_PRACTICA_CAMIONES",
}
datos = {
"camion_id": "CAM-0001-2026",
"latitud": 19.5438,
"longitud": -96.9102,
"velocidad": 42.5,
"registrado_en": "2026-05-24T10:30:00",
}
respuesta = requests.post(url, json=datos, headers=headers)
print("Código:", respuesta.status_code)
print("Respuesta:", respuesta.json())
