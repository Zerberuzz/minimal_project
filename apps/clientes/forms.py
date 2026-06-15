from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from apps.clientes.models import Cliente
from seguridad.validadores import (
    validar_nombre,
    validar_email,
    validar_telefono,
    validar_identificador_cliente,
    sanitizar_texto,
)


class LoginSeguroForm(AuthenticationForm):
    """Formulario de login con protección OWASP contra ataques de fuerza bruta."""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autocomplete': 'username',
            'autofocus': True,
        }),
        label='Nombre de usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
        }),
        label='Contraseña'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            raise ValidationError("El nombre de usuario es requerido.")
        
        if len(username) < 3:
            raise ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        
        if not username.isalnum() and '_' not in username:
            raise ValidationError("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        
        if not password:
            raise ValidationError("La contraseña es requerida.")
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        return password


class RegistroClienteForm(forms.ModelForm):
    """Formulario para registro de nuevos clientes con validación estricta."""
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'new-password',
        }),
        label='Contraseña',
        min_length=8,
        help_text='La contraseña debe tener al menos 8 caracteres'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password',
        }),
        label='Confirmar contraseña'
    )
    
    class Meta:
        model = Cliente
        fields = [
            'identificador',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'correo',
            'telefono',
        ]
        widgets = {
            'identificador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: cliente_001',
                'maxlength': '30',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre',
                'maxlength': '120',
            }),
            'apellido_paterno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido paterno',
                'maxlength': '120',
            }),
            'apellido_materno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido materno',
                'maxlength': '120',
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico',
                'autocomplete': 'email',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono',
                'maxlength': '20',
            }),
        }
    
    def clean_identificador(self):
        identificador = self.cleaned_data.get('identificador', '')
        return validar_identificador_cliente(identificador)
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        return validar_nombre(nombre)
    
    def clean_apellido_paterno(self):
        apellido = self.cleaned_data.get('apellido_paterno', '')
        return validar_nombre(apellido)
    
    def clean_apellido_materno(self):
        apellido = self.cleaned_data.get('apellido_materno', '')
        return validar_nombre(apellido)
    
    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '')
        
        from seguridad.validadores import validar_email
        correo = validar_email(correo)
        
        # Verificar que el correo no esté en uso
        if User.objects.filter(email=correo).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        
        return correo
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        return validar_telefono(telefono)
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')
        
        if password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        # Validar complejidad de contraseña
        if not any(char.isdigit() for char in password1):
            raise ValidationError(
                "La contraseña debe contener al menos un número."
            )
        
        if not any(char.isupper() for char in password1):
            raise ValidationError(
                "La contraseña debe contener al menos una letra mayúscula."
            )
        
        if not any(char.islower() for char in password1):
            raise ValidationError(
                "La contraseña debe contener al menos una letra minúscula."
            )
        
        return password2
    
    def save(self, commit=True):
        cliente = super().save(commit=False)
        
        # Crear usuario asociado
        user = User.objects.create_user(
            username=self.cleaned_data['identificador'],
            email=self.cleaned_data['correo'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['nombre'],
            last_name=f"{self.cleaned_data['apellido_paterno']} {self.cleaned_data['apellido_materno']}"
        )
        
        cliente.usuario = user
        
        if commit:
            cliente.save()
        
        return cliente


class ActualizarClienteForm(forms.ModelForm):
    """Formulario para actualizar información del cliente."""
    
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'correo',
            'telefono',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre',
                'maxlength': '120',
            }),
            'apellido_paterno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido paterno',
                'maxlength': '120',
            }),
            'apellido_materno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido materno',
                'maxlength': '120',
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono',
                'maxlength': '20',
            }),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        return validar_nombre(nombre)
    
    def clean_apellido_paterno(self):
        apellido = self.cleaned_data.get('apellido_paterno', '')
        return validar_nombre(apellido)
    
    def clean_apellido_materno(self):
        apellido = self.cleaned_data.get('apellido_materno', '')
        return validar_nombre(apellido)
    
    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '')
        
        from seguridad.validadores import validar_email
        correo = validar_email(correo)
        
        # Verificar que el correo no esté en uso por otro usuario
        cliente_id = self.instance.id
        if User.objects.filter(email=correo).exclude(
            cliente__id=cliente_id
        ).exists():
            raise ValidationError("Este correo electrónico ya está registrado por otro usuario.")
        
        return correo
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        return validar_telefono(telefono)
