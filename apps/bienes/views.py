from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from seguridad.decorators import cliente_requerido, supervisor_requerido

from apps.bienes.forms import BienForm
from apps.bienes.models import Bien
# Create your views here.

@login_required
def lista_bienes(request):
    bienes = Bien.objects.all().order_by("identificador")
    return render(request, "bienes/lista.html", {"bienes": bienes})


@login_required
@cliente_requerido
def crear_bien(request):
    if request.method == "POST":
        form = BienForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("bienes:lista")
    else:
        form = BienForm()

    return render(request, "bienes/formulario.html", {"form": form})

@login_required
@supervisor_requerido
def reporte_general_bienes(request):
    bienes = Bien.objects.all().order_by('identificador')
    total_bienes = bienes.count()
    
    context = {
        "bienes": bienes,
        "total_bienes": total_bienes,
    }
    return render(request, "bienes/reporte_general.html", context)