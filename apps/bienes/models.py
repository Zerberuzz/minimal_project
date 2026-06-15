import html
from django.db import models
from django.core.exceptions import ValidationError
from apps.clientes.models import Cliente
from seguridad.validadores import (
    validar_descripcion_bien,
    sanitizar_descripcion,
    validar_valor_bien,
    validar_estatus_bien,
    validar_latitud,
    validar_longitud,
    validar_identificador_camion,
)


class Direccion(models.Model):
    """
    Modelo para almacenar direcciones de recolección y entrega.
    Utiliza validación y sanitización estricta de datos.
    """
    
    calle = models.CharField(
        max_length=150,
        help_text='Nombre de la calle'
    )
    
    numero_exterior = models.CharField(
        max_length=20,
        help_text='Número exterior de la dirección'
    )
    
    numero_interior = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text='Número interior (opcional)'
    )
    
    ciudad = models.CharField(
        max_length=100,
        help_text='Ciudad'
    )
    
    codigo_postal = models.CharField(
        max_length=10,
        help_text='Código postal'
    )
    
    estado = models.CharField(
        max_length=100,
        help_text='Estado o provincia'
    )
    
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Latitud de la dirección'
    )
    
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Longitud de la dirección'
    )
    
    notas_adicionales = models.TextField(
        blank=True,
        default='',
        max_length=500,
        help_text='Notas adicionales de la dirección'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
    
    def __str__(self):
        interior_str = f" {self.numero_interior}" if self.numero_interior else ""
        return f"{self.calle} {self.numero_exterior}{interior_str}, {self.ciudad}"
    
    def clean(self):
        """Valida y sanitiza los datos de la dirección."""
        from seguridad.validadores import (
            validar_calle,
            validar_numero_exterior,
            validar_numero_interior,
            validar_ciudad,
            validar_codigo_postal,
            validar_estado,
            validar_latitud,
            validar_longitud,
        )
        
        try:
            self.calle = validar_calle(self.calle)
            self.numero_exterior = validar_numero_exterior(self.numero_exterior)
            self.numero_interior = validar_numero_interior(self.numero_interior)
            self.ciudad = validar_ciudad(self.ciudad)
            self.codigo_postal = validar_codigo_postal(self.codigo_postal)
            self.estado = validar_estado(self.estado)
            self.latitud = validar_latitud(self.latitud)
            self.longitud = validar_longitud(self.longitud)
            
            if self.notas_adicionales:
                from seguridad.validadores import sanitizar_entrada_general
                self.notas_adicionales = sanitizar_entrada_general(
                    self.notas_adicionales,
                    max_length=500
                )
        except ValidationError as e:
            raise e


class Bien(models.Model):
    """
    Modelo de bienes logísticos.
    Vinculado a un cliente y con direcciones de recolección y entrega.
    """
    
    ESTATUS_CHOICES = [
        ('Registrado', 'Registrado'),
        ('En tránsito', 'En tránsito'),
        ('Entregado', 'Entregado'),
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='bienes'
    )
    
    direccion_recoleccion = models.ForeignKey(
        Direccion,
        on_delete=models.PROTECT,
        related_name='bienes_recoleccion',
        null=True,
        blank=True,
        help_text='Dirección de recolección del bien'
    )
    
    direccion_entrega = models.ForeignKey(
        Direccion,
        on_delete=models.PROTECT,
        related_name='bienes_entrega',
        null=True,
        blank=True,
        help_text='Dirección de entrega del bien'
    )
    
    identificador = models.CharField(
        max_length=20,
        unique=True,
        help_text='Identificador único del bien (b-XXXX-YYYY)'
    )
    
    descripcion = models.CharField(
        max_length=500,
        help_text='Descripción detallada del bien'
    )
    
    marca = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Marca o fabricante del bien'
    )
    
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Valor del bien en pesos'
    )
    
    estatus = models.CharField(
        max_length=50,
        choices=ESTATUS_CHOICES,
        default='Registrado',
        help_text='Estado actual del bien'
    )
    
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de última actualización'
    )
    
    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Bien'
        verbose_name_plural = 'Bienes'
        indexes = [
            models.Index(fields=['cliente', 'estatus']),
            models.Index(fields=['-creado_en']),
        ]
    
    def __str__(self):
        return f"{self.identificador} - {self.cliente.nombre_completo}"
    
    def clean(self):
        """Valida y sanitiza los datos del bien."""
        try:
            self.descripcion = validar_descripcion_bien(self.descripcion)
            self.descripcion = sanitizar_descripcion(self.descripcion)
            self.valor = validar_valor_bien(self.valor)
            self.estatus = validar_estatus_bien(self.estatus)
            
            if self.marca:
                from seguridad.validadores import sanitizar_entrada_general
                self.marca = sanitizar_entrada_general(self.marca, max_length=100)
        except ValidationError as e:
            raise e


class CamionGPS(models.Model):
    """
    Modelo para registrar coordenadas GPS de camiones en tiempo real.
    Propósito: Auditoría y no repudio de rastreo de vehículos.
    """
    
    identificador_camion = models.CharField(
        max_length=20,
        help_text='Identificador único del camión'
    )
    
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Latitud del camión'
    )
    
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Longitud del camión'
    )
    
    fecha_hora = models.DateTimeField(
        help_text='Fecha y hora de la actualización GPS'
    )
    
    validado = models.BooleanField(
        default=False,
        help_text='Indica si las coordenadas fueron validadas'
    )
    
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Registro GPS'
        verbose_name_plural = 'Registros GPS'
        indexes = [
            models.Index(fields=['identificador_camion', 'fecha_hora']),
            models.Index(fields=['fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.identificador_camion} - {self.fecha_hora}"
    
    def clean(self):
        """Valida y sanitiza los datos GPS."""
        try:
            self.identificador_camion = validar_identificador_camion(
                self.identificador_camion
            )
            self.latitud = validar_latitud(self.latitud)
            self.longitud = validar_longitud(self.longitud)
        except ValidationError as e:
            raise e