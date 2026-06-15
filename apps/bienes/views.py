import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from seguridad.decorators import (
    cliente_requerido,
    supervisor_requerido,
    solo_post,
    proteger_bien_id,
    validar_token_api,
    supervisor_solo_lectura,
)
from seguridad.roles import es_cliente, es_supervisor
from seguridad.utils import (
    registrar_creacion_bien,
    registrar_actualizacion_bien,
    registrar_consulta_reporte,
    registrar_gps_valida,
    registrar_gps_rechazada,
    registrar_acceso_no_autorizado,
    obtener_ip_cliente,
)
from seguridad.models import Bitacora
from apps.bienes.forms import BienForm, DireccionForm, CamionGPSForm
from apps.bienes.models import Bien, Direccion, CamionGPS
from apps.clientes.models import Cliente


@require_http_methods(["GET"])
@login_required
def lista_bienes(request):
    """
    Lista bienes del cliente actual.
    Si es supervisor, lista todos los bienes.
    """
    if es_supervisor(request.user):
        bienes = Bien.objects.all().order_by('-creado_en')
    elif es_cliente(request.user):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        bienes = Bien.objects.filter(cliente=cliente).order_by('-creado_en')
    else:
        raise PermissionDenied("No tienes permiso para ver esta página.")
    
    context = {
        'bienes': bienes,
        'total': bienes.count(),
    }
    
    return render(request, 'bienes/lista.html', context)


@require_http_methods(["GET", "POST"])
@login_required
@cliente_requerido
def crear_bien(request):
    """
    Crea un nuevo bien para el cliente actual.
    Solo accesible por clientes.
    """
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    if request.method == "POST":
        form = BienForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    bien = form.save(commit=False)
                    bien.cliente = cliente
                    bien.full_clean()
                    bien.save()
                    
                    registrar_creacion_bien(
                        request.user,
                        bien.identificador,
                        request
                    )
                    
                    messages.success(
                        request,
                        f'Bien "{bien.identificador}" creado exitosamente.'
                    )
                    
                    return redirect('bienes:lista')
                    
            except ValidationError as e:
                messages.error(request, f'Error de validación: {e.message}')
            except Exception as e:
                messages.error(request, f'Error al crear el bien: {str(e)}')
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f'{campo}: {error}')
    else:
        form = BienForm()
    
    context = {
        'form': form,
        'cliente': cliente,
        'titulo': 'Registrar Nuevo Bien',
    }
    
    return render(request, 'bienes/formulario.html', context)


@require_http_methods(["GET", "POST"])
@login_required
@proteger_bien_id
def actualizar_bien(request, bien_id):
    """
    Actualiza un bien existente.
    Los clientes solo pueden actualizar sus propios bienes.
    Los supervisores solo pueden ver (lectura).
    """
    bien = get_object_or_404(Bien, id=bien_id)
    
    # Protección contra IDOR (Insecure Direct Object Reference)
    if es_cliente(request.user):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        if bien.cliente != cliente:
            registrar_acceso_no_autorizado(
                request.user,
                'actualizar_bien',
                f'Intento de actualizar bien ajeno (bien_id={bien_id})',
                request
            )
            raise PermissionDenied(
                "No tienes permiso para actualizar este bien."
            )
    elif es_supervisor(request.user):
        raise PermissionDenied(
            "Los supervisores no pueden actualizar bienes."
        )
    else:
        raise PermissionDenied(
            "No tienes permiso para acceder a esta acción."
        )
    
    if request.method == "POST":
        form = BienForm(request.POST, instance=bien)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    bien_actualizado = form.save(commit=False)
                    bien_actualizado.full_clean()
                    bien_actualizado.save()
                    
                    cambios = {
                        'descripcion': bien_actualizado.descripcion,
                        'valor': str(bien_actualizado.valor),
                        'estatus': bien_actualizado.estatus,
                    }
                    
                    registrar_actualizacion_bien(
                        request.user,
                        bien.identificador,
                        cambios,
                        request
                    )
                    
                    messages.success(
                        request,
                        f'Bien "{bien.identificador}" actualizado exitosamente.'
                    )
                    
                    return redirect('bienes:lista')
                    
            except ValidationError as e:
                messages.error(request, f'Error de validación: {e.message}')
            except Exception as e:
                messages.error(request, f'Error al actualizar el bien: {str(e)}')
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f'{campo}: {error}')
    else:
        form = BienForm(instance=bien)
    
    context = {
        'form': form,
        'bien': bien,
        'titulo': f'Actualizar Bien: {bien.identificador}',
    }
    
    return render(request, 'bienes/formulario.html', context)


@require_http_methods(["GET"])
@login_required
def reporte_mis_bienes(request):
    """
    Reporte de bienes del cliente actual.
    Solo accesible por el cliente dueño de los bienes.
    """
    if not es_cliente(request.user):
        raise PermissionDenied(
            "Solo los clientes pueden ver sus reportes."
        )
    
    cliente = get_object_or_404(Cliente, usuario=request.user)
    bienes = Bien.objects.filter(cliente=cliente).order_by('-creado_en')
    
    registrar_consulta_reporte(
        request.user,
        'reporte_mis_bienes',
        request
    )
    
    estadisticas = {
        'total_bienes': bienes.count(),
        'registrados': bienes.filter(estatus='Registrado').count(),
        'en_transito': bienes.filter(estatus='En tránsito').count(),
        'entregados': bienes.filter(estatus='Entregado').count(),
        'valor_total': sum(b.valor for b in bienes),
    }
    
    context = {
        'bienes': bienes,
        'cliente': cliente,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'bienes/reporte_cliente.html', context)


@require_http_methods(["GET"])
@login_required
@supervisor_requerido
@supervisor_solo_lectura
def reporte_general_bienes(request):
    """
    Reporte general de todos los bienes.
    Solo accesible por supervisores en lectura.
    """
    bienes = Bien.objects.select_related('cliente').all().order_by('-creado_en')
    clientes = Cliente.objects.all()
    
    registrar_consulta_reporte(
        request.user,
        'reporte_general_bienes',
        request
    )
    
    estadisticas = {
        'total_bienes': bienes.count(),
        'total_clientes': clientes.count(),
        'registrados': bienes.filter(estatus='Registrado').count(),
        'en_transito': bienes.filter(estatus='En tránsito').count(),
        'entregados': bienes.filter(estatus='Entregado').count(),
        'valor_total': sum(b.valor for b in bienes),
    }
    
    context = {
        'bienes': bienes,
        'clientes': clientes,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'bienes/reporte_general.html', context)


@require_http_methods(["GET"])
@login_required
@supervisor_requerido
@supervisor_solo_lectura
def ver_bitacora(request):
    """
    Vista de bitácora de auditoría.
    Solo accesible por supervisores.
    """
    registros = Bitacora.objects.all().order_by('-fecha_hora')[:500]
    
    registrar_consulta_reporte(
        request.user,
        'bitacora_auditoria',
        request
    )
    
    # Filtros opcionales
    usuario_id = request.GET.get('usuario_id')
    accion = request.GET.get('accion')
    resultado = request.GET.get('resultado')
    
    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)
    
    if accion:
        registros = registros.filter(accion=accion)
    
    if resultado:
        registros = registros.filter(resultado=resultado)
    
    context = {
        'registros': registros,
        'total': registros.count(),
    }
    
    return render(request, 'bienes/bitacora.html', context)


@require_http_methods(["GET", "POST"])
@login_required
def crear_direccion(request):
    """
    Crea una nueva dirección.
    Accesible por clientes para sus propias direcciones.
    """
    if not es_cliente(request.user):
        raise PermissionDenied(
            "Solo los clientes pueden crear direcciones."
        )
    
    if request.method == "POST":
        form = DireccionForm(request.POST)
        
        if form.is_valid():
            try:
                direccion = form.save(commit=False)
                direccion.full_clean()
                direccion.save()
                
                messages.success(
                    request,
                    f'Dirección creada exitosamente.'
                )
                
                return redirect('bienes:lista')
                
            except ValidationError as e:
                messages.error(request, f'Error de validación: {e.message}')
            except Exception as e:
                messages.error(
                    request,
                    f'Error al crear la dirección: {str(e)}'
                )
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f'{campo}: {error}')
    else:
        form = DireccionForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nueva Dirección',
    }
    
    return render(request, 'bienes/formulario_direccion.html', context)


@require_http_methods(["POST"])
@login_required
@proteger_bien_id
def eliminar_bien(request, bien_id):
    """
    Elimina un bien existente.
    Los clientes solo pueden eliminar sus propios bienes.
    """
    bien = get_object_or_404(Bien, id=bien_id)
    
    # Protección contra IDOR (Insecure Direct Object Reference)
    if es_cliente(request.user):
        cliente = get_object_or_404(Cliente, usuario=request.user)
        if bien.cliente != cliente:
            registrar_acceso_no_autorizado(
                request.user,
                'eliminar_bien',
                f'Intento de eliminar bien ajeno (bien_id={bien_id})',
                request
            )
            raise PermissionDenied(
                "No tienes permiso para eliminar este bien."
            )
    else:
        raise PermissionDenied(
            "Solo los clientes pueden eliminar bienes."
        )
    
    try:
        with transaction.atomic():
            identificador_bien = bien.identificador
            bien.delete()
            
            registrar_eliminacion_bien(
                request.user,
                identificador_bien,
                request
            )
            
            messages.success(
                request,
                f'Bien "{identificador_bien}" eliminado exitosamente.'
            )
    except Exception as e:
        messages.error(request, f'Error al eliminar el bien: {str(e)}')
        
    return redirect('bienes:lista')


@require_http_methods(["POST"])
@validar_token_api
@require_http_methods(["POST"])
def actualizar_gps_camion(request):
    """
    Endpoint seguro para actualizar coordenadas GPS de camiones.
    Requiere autenticación por token en header Authorization.
    Registra todas las operaciones en bitácora.
    """
    try:
        datos = json.loads(request.body)
        
        camion_id = datos.get('identificador_camion', '').strip()
        latitud = datos.get('latitud')
        longitud = datos.get('longitud')
        fecha_hora_str = datos.get('fecha_hora')
        
        # Validación de datos
        if not all([camion_id, latitud, longitud, fecha_hora_str]):
            registrar_gps_rechazada(
                camion_id or 'desconocido',
                'Campos requeridos faltantes',
                request
            )
            
            return JsonResponse({
                'error': 'Faltan campos requeridos',
                'campos_requeridos': [
                    'identificador_camion',
                    'latitud',
                    'longitud',
                    'fecha_hora'
                ]
            }, status=400)
        
        # Usar formulario para validar
        form = CamionGPSForm(datos)
        
        if not form.is_valid():
            errores = '; '.join([
                f"{campo}: {', '.join(msgs)}"
                for campo, msgs in form.errors.items()
            ])
            
            registrar_gps_rechazada(
                camion_id,
                f'Validación fallida: {errores}',
                request
            )
            
            return JsonResponse({
                'error': 'Validación de datos fallida',
                'detalles': form.errors
            }, status=400)
        
        # Crear registro GPS
        try:
            fecha_hora = timezone.datetime.fromisoformat(fecha_hora_str)
        except:
            fecha_hora = timezone.now()
        
        camion_gps = CamionGPS(
            identificador_camion=form.cleaned_data['identificador_camion'],
            latitud=form.cleaned_data['latitud'],
            longitud=form.cleaned_data['longitud'],
            fecha_hora=fecha_hora,
            validado=True
        )
        
        camion_gps.save()
        
        registrar_gps_valida(
            form.cleaned_data['identificador_camion'],
            form.cleaned_data['latitud'],
            form.cleaned_data['longitud'],
            request
        )
        
        return JsonResponse({
            'exitoso': True,
            'mensaje': 'Actualización GPS registrada exitosamente',
            'gps_id': camion_gps.id,
        }, status=201)
        
    except json.JSONDecodeError:
        registrar_gps_rechazada(
            'desconocido',
            'JSON inválido',
            request
        )
        
        return JsonResponse({
            'error': 'Formato JSON inválido'
        }, status=400)
        
    except Exception as e:
        registrar_gps_rechazada(
            'desconocido',
            f'Error interno: {str(e)}',
            request
        )
        
        return JsonResponse({
            'error': 'Error interno del servidor'
        }, status=500)