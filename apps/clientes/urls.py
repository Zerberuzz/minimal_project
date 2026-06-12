from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('perfil/', views.perfil_view, name='perfil'),
]
