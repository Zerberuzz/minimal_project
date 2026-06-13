from django.urls import path
from . import views

urlpatterns = [
    path("bienes/", views.lista_bienes, name="lista_bienes"),
    path("bienes/nuevo/", views.crear_bien, name="crear_bien"),
    path(
        "bienes/mis-bienes/",
        views.reporte_mis_bienes,
        name="reporte_mis_bienes"
    ),
    path(
        "bienes/reporte-general/",
        views.reporte_general_bienes,
        name="reporte_general_bienes"
    ),
]