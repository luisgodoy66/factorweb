from enum import unique
from django.db import models
from django.forms import DateField
from bases.models import ClaseModelo
from datetime import date

class Bancos(ClaseModelo):
    ctbanco =models.TextField()
    llocal = models.BooleanField(default=True)

    def __str__(self):
        return self.ctbanco

class Feriados(ClaseModelo):
    dferiado = models.DateField()
    llaborable = models.BooleanField(default=False)

    def __str__(self):
        # return date.isoformat(self.dferiado)
        return self.dferiado.strftime("%Y-%m-%d") 
    
class Actividades(ClaseModelo):
    cxactividad = models.CharField(max_length=10)
    ctactividad = models.TextField()    

    def __str__(self):
        return "{} {}".format(self.cxactividad, self.ctactividad)