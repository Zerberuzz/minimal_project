from django import forms
from .models import Bien

from seguridad.validadores import validar_identificador_bien

class BienForm(forms.ModelForm):
    class Meta:
        model = Bien
        fields = [
            "identificador",
            "descripcion",
            "marca",
            "valor",
            "estatus",
        ]

    def clean_identificador(self):
        identificador = self.cleaned_data["identificador"].strip()
        validar_identificador_bien(identificador)
        return identificador

    def clean_descripcion(self):
        descripcion = self.cleaned_data["descripcion"]
        # return validar_descripcion(descripcion)
        return descripcion

    def clean_marca(self):
        marca = self.cleaned_data["marca"]
        # return validar_marca(marca)
        return marca

    def clean_valor(self):
        valor = self.cleaned_data["valor"]
        # return validar_valor(valor)
        return valor
        