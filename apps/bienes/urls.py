from django.urls import path
from . import views
app_name = "bienes"
urlpatterns = [
path("", views.lista_bienes, name="lista"),
path("nuevo/", views.crear_bien, name="crear"),
path("reporte-general/", views.reporte_general_bienes, name="reporte_general_bienes")
]