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
    
class Provincias(ClaseModelo):
    cxprovincia = models.CharField(max_length=10, null=True, blank=True)
    ctprovincia = models.CharField(max_length=50)

    def __str__(self):
        return self.ctprovincia
    
class Cantones(ClaseModelo):
    provincia = models.ForeignKey(Provincias, on_delete=models.CASCADE)
    cxcanton = models.CharField(max_length=10, null=True, blank=True)
    ctcanton = models.CharField(max_length=50)

    def __str__(self):
        return self.ctcanton    