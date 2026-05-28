from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "identificador",
        "nombre",
        "apellido_paterno",
        "apellido_materno",
        "correo",
        "telefono",
        "usuario",
        "creado_en",
        "actualizado_en",
    )
    search_fields = (
        "identificador",
        "nombre",
        "apellido_paterno",
        "apellido_materno",
        "correo",
    )
    list_filter = ("creado_en",)