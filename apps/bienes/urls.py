from django.urls import path
from . import views

app_name = 'bienes'

urlpatterns = [
    # Listado de bienes
    path('', views.lista_bienes, name='lista'),
    
    # Crear bien
    path('nuevo/', views.crear_bien, name='crear'),
    
    # Actualizar bien
    path('<int:bien_id>/editar/', views.actualizar_bien, name='editar'),
    path('<int:bien_id>/eliminar/', views.eliminar_bien, name='eliminar'),
    
    # Reportes
    path('mis-bienes/', views.reporte_mis_bienes, name='reporte_mis_bienes'),
    path('reporte-general/', views.reporte_general_bienes, name='reporte_general_bienes'),
    
    # Bitácora
    path('bitacora/', views.ver_bitacora, name='bitacora'),
    
    # Direcciones
    path('direccion/nueva/', views.crear_direccion, name='crear_direccion'),
    
    # API GPS (con token)
    path('api/gps/', views.actualizar_gps_camion, name='api_gps'),
]