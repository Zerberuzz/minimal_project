from django.contrib import admin
from seguridad.models import Bitacora


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    """Interfaz admin para visualizar y filtrar la bitácora de auditoría."""
    
    list_display = [
        'fecha_hora',
        'usuario',
        'rol',
        'accion',
        'resultado',
        'ip_origen',
    ]
    
    list_filter = [
        'fecha_hora',
        'accion',
        'resultado',
        'rol',
    ]
    
    search_fields = [
        'usuario__username',
        'ip_origen',
        'descripcion',
        'ruta',
    ]
    
    readonly_fields = [
        'fecha_hora',
        'usuario',
        'rol',
        'accion',
        'resultado',
        'descripcion',
        'ip_origen',
        'metodo_http',
        'ruta',
        'datos_adicionales',
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
