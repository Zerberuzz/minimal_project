from django.db import models
from django.contrib.auth.models import User


class Bitacora(models.Model):
    """
    Modelo de auditoría y no repudio.
    Registra todas las acciones importantes del sistema con propósitos de auditoría.
    """
    
    RESULTADO_CHOICES = [
        ('exitoso', 'Exitoso'),
        ('rechazado', 'Rechazado'),
        ('error', 'Error'),
    ]
    
    ACCION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('login_fallido', 'Intento fallido de inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('crear_bien', 'Crear bien'),
        ('actualizar_bien', 'Actualizar bien'),
        ('eliminar_bien', 'Eliminar bien'),
        ('crear_direccion', 'Crear dirección'),
        ('actualizar_direccion', 'Actualizar dirección'),
        ('consultar_reporte', 'Consultar reporte'),
        ('consultar_bitacora', 'Consultar bitácora'),
        ('actualizar_gps', 'Actualización GPS'),
        ('acceso_no_autorizado', 'Intento de acceso no autorizado'),
        ('acceso_denegado', 'Acceso denegado'),
        ('alta_cliente', 'Alta de cliente'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bitacora_acciones'
    )
    
    rol = models.CharField(
        max_length=50,
        default='anonimo',
        help_text='Rol del usuario que realizó la acción'
    )
    
    accion = models.CharField(
        max_length=50,
        choices=ACCION_CHOICES,
        help_text='Tipo de acción realizada'
    )
    
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='exitoso',
        help_text='Resultado de la acción'
    )
    
    descripcion = models.TextField(
        help_text='Detalles adicionales de la acción'
    )
    
    ip_origen = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Dirección IP del origen de la solicitud'
    )
    
    metodo_http = models.CharField(
        max_length=10,
        default='GET',
        help_text='Método HTTP utilizado'
    )
    
    ruta = models.CharField(
        max_length=500,
        help_text='Ruta o endpoint accedido'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales en formato JSON para auditoría'
    )
    
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora exacta de la acción'
    )
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        indexes = [
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['usuario', 'fecha_hora']),
            models.Index(fields=['accion']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'anónimo'
        return f"[{self.fecha_hora}] {usuario_str} - {self.get_accion_display()}"
