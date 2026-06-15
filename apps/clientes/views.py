from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from apps.clientes.forms import (
    LoginSeguroForm,
    RegistroClienteForm,
    ActualizarClienteForm,
)
from apps.clientes.models import Cliente
from seguridad.roles import asignar_rol_cliente, crear_grupos_si_no_existen
from seguridad.utils import (
    registrar_login_exitoso,
    registrar_login_fallido,
    registrar_alta_cliente_exitoso,
    registrar_alta_cliente_rechazada,
)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista de login segura con protección contra ataques.
    Registra intentos exitosos y fallidos en bitácora.
    """
    if request.method == "POST":
        form = LoginSeguroForm(request, data=request.POST)
        
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            registrar_login_exitoso(usuario, request)
            
            messages.success(
                request,
                f'Bienvenido, {usuario.first_name or usuario.username}!'
            )
            
            return redirect('bienes:lista')
        else:
            username = request.POST.get('username', '')
            registrar_login_fallido(username, request)
            
            messages.error(
                request,
                'Nombre de usuario o contraseña incorrectos.'
            )
    else:
        form = LoginSeguroForm()
    
    return render(request, 'registration/login.html', {'form': form})


@require_http_methods(["POST"])
@login_required
def logout_view(request):
    """
    Vista de logout que destruye la sesión de forma segura.
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@require_http_methods(["GET", "POST"])
def registro_view(request):
    """
    Vista de registro de nuevos clientes con validación estricta.
    """
    if request.user.is_authenticated:
        return redirect('bienes:lista')
    
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        
        if form.is_valid():
            cliente = form.save(commit=False)
            crear_grupos_si_no_existen()
            asignar_rol_cliente(cliente.usuario)
            cliente.save()
            registrar_alta_cliente_exitoso(cliente.usuario, request)
            
            messages.success(
                request,
                'Registro exitoso. Por favor, inicia sesión.'
            )
            
            return redirect('login')
        else:
            username = form.data.get('username', '')
            registrar_alta_cliente_rechazada(
                username,
                'Errores de validación en el formulario de registro',
                request
            )
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f'{campo}: {error}')
    else:
        form = RegistroClienteForm()
    
    return render(request, 'clientes/registro.html', {'form': form})


@require_http_methods(["GET", "POST"])
@login_required
def perfil_view(request):
    """
    Vista para ver y actualizar el perfil del cliente.
    """
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        raise PermissionDenied(
            "No tienes un perfil de cliente asociado."
        )
    
    if request.method == "POST":
        form = ActualizarClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Tu perfil ha sido actualizado correctamente.'
            )
            return redirect('clientes:perfil')
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f'{campo}: {error}')
    else:
        form = ActualizarClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
    }
    
    return render(request, 'clientes/perfil.html', context)
