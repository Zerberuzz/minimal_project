from django.contrib import admin
from django.urls import path, include
from apps.clientes import views as clientes_views
from apps.bienes import views as bienes_views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='inicio'),

    path('admin/', admin.site.urls),
    
    # Autenticación de clientes
    path('login/', clientes_views.login_view, name='login'),
    path('logout/', clientes_views.logout_view, name='logout'),
    path('registro/', clientes_views.registro_view, name='registro'),
    path('perfil/', clientes_views.perfil_view, name='perfil'),
    
    # URLs de bienes
    path('bienes/', include('apps.bienes.urls')),
    
    # Clientes
    path('clientes/', include('apps.clientes.urls')),
    
    # API Rastreo
    path('api/', include('apps.rastreo.urls')),
]
