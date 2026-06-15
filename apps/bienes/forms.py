from django import forms
from django.core.exceptions import ValidationError
from apps.bienes.models import Bien, Direccion, CamionGPS
from seguridad.validadores import (
    validar_descripcion_bien,
    validar_valor_bien,
    validar_estatus_bien,
    validar_identificador_bien,
    validar_calle,
    validar_numero_exterior,
    validar_numero_interior,
    validar_ciudad,
    validar_codigo_postal,
    validar_estado,
    validar_latitud,
    validar_longitud,
    validar_identificador_camion,
    sanitizar_descripcion,
)


class DireccionForm(forms.ModelForm):
    """Formulario para crear y actualizar direcciones con validación estricta."""
    
    class Meta:
        model = Direccion
        fields = [
            'calle',
            'numero_exterior',
            'numero_interior',
            'ciudad',
            'codigo_postal',
            'estado',
            'latitud',
            'longitud',
            'notas_adicionales',
        ]
        widgets = {
            'calle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Avenida Principal',
                'maxlength': '150',
            }),
            'numero_exterior': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 123',
                'maxlength': '20',
            }),
            'numero_interior': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Apt 4B',
                'maxlength': '20',
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Xalapa',
                'maxlength': '100',
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 91000',
                'maxlength': '10',
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Veracruz',
                'maxlength': '100',
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 19.543095',
                'step': '0.000001',
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -96.911132',
                'step': '0.000001',
            }),
            'notas_adicionales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)',
                'maxlength': '500',
            }),
        }
    
    def clean_calle(self):
        calle = self.cleaned_data.get('calle', '')
        return validar_calle(calle)
    
    def clean_numero_exterior(self):
        numero_exterior = self.cleaned_data.get('numero_exterior', '')
        return validar_numero_exterior(numero_exterior)
    
    def clean_numero_interior(self):
        numero_interior = self.cleaned_data.get('numero_interior', '')
        return validar_numero_interior(numero_interior)
    
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad', '')
        return validar_ciudad(ciudad)
    
    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal', '')
        return validar_codigo_postal(codigo_postal)
    
    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '')
        return validar_estado(estado)
    
    def clean_latitud(self):
        latitud = self.cleaned_data.get('latitud')
        return validar_latitud(latitud)
    
    def clean_longitud(self):
        longitud = self.cleaned_data.get('longitud')
        return validar_longitud(longitud)


class BienForm(forms.ModelForm):
    """Formulario para crear y actualizar bienes con validación estricta."""
    
    direccion_recoleccion = forms.ModelChoiceField(
        queryset=Direccion.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Dirección de Recolección'
    )
    
    direccion_entrega = forms.ModelChoiceField(
        queryset=Direccion.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Dirección de Entrega'
    )
    
    class Meta:
        model = Bien
        fields = [
            'identificador',
            'descripcion',
            'marca',
            'valor',
            'estatus',
            'direccion_recoleccion',
            'direccion_entrega',
        ]
        widgets = {
            'identificador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: b-0001-2024',
                'maxlength': '20',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del bien...',
                'maxlength': '500',
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Samsung',
                'maxlength': '100',
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 5000.00',
                'step': '0.01',
            }),
            'estatus': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def clean_identificador(self):
        identificador = self.cleaned_data.get('identificador', '')
        return validar_identificador_bien(identificador)
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '')
        descripcion = validar_descripcion_bien(descripcion)
        return sanitizar_descripcion(descripcion)
    
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        return validar_valor_bien(valor)
    
    def clean_estatus(self):
        estatus = self.cleaned_data.get('estatus', '')
        return validar_estatus_bien(estatus)


class CamionGPSForm(forms.ModelForm):
    """Formulario para registrar posiciones GPS de camiones."""
    
    class Meta:
        model = CamionGPS
        fields = [
            'identificador_camion',
            'latitud',
            'longitud',
            'fecha_hora',
        ]
        widgets = {
            'identificador_camion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CAMION-001',
                'maxlength': '20',
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 19.543095',
                'step': '0.000001',
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -96.911132',
                'step': '0.000001',
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }
    
    def clean_identificador_camion(self):
        identificador = self.cleaned_data.get('identificador_camion', '')
        return validar_identificador_camion(identificador)
    
    def clean_latitud(self):
        latitud = self.cleaned_data.get('latitud')
        return validar_latitud(latitud)
    
    def clean_longitud(self):
        longitud = self.cleaned_data.get('longitud')
        return validar_longitud(longitud)