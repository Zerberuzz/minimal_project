from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from seguridad.decorators import cliente_requerido, supervisor_requerido
from seguridad.roles import es_cliente, es_supervisor

from apps.bienes.forms import BienForm
from apps.bienes.models import Bien

@login_required
def lista_bienes(request):
    if es_supervisor(request.user):
        bienes = Bien.objects.select_related("cliente").all()
    elif es_cliente(request.user):
        bienes = Bien.objects.filter(
            cliente__usuario=request.user
        )
    else:
        bienes = Bien.objects.none()

    return render(
        request,
        "bienes/lista_bienes.html",
        {
            "bienes": bienes,
            "es_cliente": es_cliente(request.user),
            "es_supervisor": es_supervisor(request.user),
        }
    )

@login_required
@cliente_requerido
def crear_bien(request):
    cliente = request.user.cliente
    if request.method == "POST":
        form = BienForm(request.POST)
        if form.is_valid():
            bien = form.save(commit=False)
            bien.cliente = cliente
            bien.save()
            return redirect("reporte_mis_bienes")
    else:
        form = BienForm()
    return render(
        request,
        "bienes/crear_bien.html",
        {"form": form}
    )

@login_required
@cliente_requerido
def reporte_mis_bienes(request):
    bienes = Bien.objects.filter(
        cliente__usuario=request.user
    ).order_by("-creado_en")
    return render(
        request,
        "bienes/reporte_mis_bienes.html",
        {"bienes": bienes}
    )

@login_required
@supervisor_requerido
def reporte_general_bienes(request):
    bienes = Bien.objects.select_related("cliente").order_by("-creado_en")
    return render(
        request,
        "bienes/reporte_general_bienes.html",
        {"bienes": bienes}
    )