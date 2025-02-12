from django.db import models
from bases.models import ClaseModelo

# Create your models here.
class Configuracion_slack (ClaseModelo):
    ctdescripcion = models.CharField(max_length=100)
    ctslackbottoken = models.CharField(max_length=100)
    ctslackchannelname = models.CharField(max_length=50)
    ctslacksigningsecret = models.CharField(max_length=100)
    lactivo = models.BooleanField(default=True)

    def __str__(self):
        return self.ctdescripcion

    # def save(self):
    #     self.ctdescripcion = self.ctdescripcion.upper()