from django.db import models

# Create your models here.
class UbicacionCamion(models.Model):
    camion_id = models.CharField(max_length=30)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    velocidad = models.DecimalField(max_digits=6, decimal_places=2)
    registrado_en = models.DateTimeField()
    recibido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.camion_id} - {self.registrado_en}"