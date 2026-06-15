from django.urls import path
from . import views

urlpatterns = [
    path(
        "camiones/ubicacion/",
        views.registrar_ubicacion,
        name="registrar_ubicacion"
    ),
]
