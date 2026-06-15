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
    
    # Reportes
    path('reporte-cliente/', views.reporte_bienes_cliente, name='reporte_cliente'),
    path('reporte-general/', views.reporte_general_bienes, name='reporte_general'),
    
    # Bitácora
    path('bitacora/', views.ver_bitacora, name='bitacora'),
    
    # Direcciones
    path('direccion/nueva/', views.crear_direccion, name='crear_direccion'),
    
    # API GPS (con token)
    path('api/gps/', views.actualizar_gps_camion, name='api_gps'),
]