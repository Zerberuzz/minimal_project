from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/camiones/ubicacion/",
        views.registrar_ubicacion,
        name="registrar_ubicacion"
    ),
]
