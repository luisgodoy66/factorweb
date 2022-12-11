from enum import unique
from django.db import models
from django.forms import DateField
from bases.models import ClaseModelo
from datetime import date

class Bancos(ClaseModelo):
    ctbanco =models.TextField(unique=True)
    llocal = models.BooleanField(default=True)

    def __str__(self):
        return self.ctbanco

class Feriados(ClaseModelo):
    dferiado = models.DateField(unique=True)
    llaborable = models.BooleanField(default=False)

    def __str__(self):
        # return date.isoformat(self.dferiado)
        return self.dferiado.strftime("%Y-%m-%d") 