from django.db import models

# Create your models here.
from bases.models import ClaseModelo

class Plan_cuentas(ClaseModelo):
    cxcuenta =  models.CharField( max_length=15)
    ctcuenta = models.TextField
    nnivel = models.SmallIntegerField
    ldetalle = models.BooleanField(default=False)

    def __str__(self):
        return self.ctcuenta
    
class Cuentas_especiales(ClaseModelo):
    cxcuentaporcobrar = models.CharField(max_length=15)
    cxpagoconcajachica =models.CharField(max_length=15)
    cxsobrepago = models.CharField(max_length=15)
    cxcuentaconjunta = models.CharField(max_length=15)
    cxprotesto = models.CharField(max_length=15)
    cxcuentagananciaejercicio = models.CharField(max_length=15)
    cxcuentaperdidaejercicio = models.CharField(max_length=15)
    cxcuentagananciaejercicioanterior = models.CharField(max_length=15)
    cxcuentaperdidaejercicioanterior = models.CharField(max_length=15)

class Diario_cabecera(ClaseModelo):
    cxtransaccion = models.CharField(max_length= 10) 
    ctconcepto = models.TextField
    nvalor = models.DecimalField(max_digits= 10,decimal_places= 2)
    # cxlocalidad character(2) COLLATE pg_catalog."default",
    dcontabilizado = models.DateField

    def __str__(self):
        return self.ctconcepto

class Transaccion(ClaseModelo):
    cxcuenta = models.ForeignKey(Plan_cuentas, on_delete=models.CASCADE)
    cxtipo = models.CharField( max_length=1) 
    nvalor = models.DecimalField(max_digits= 10, decimal_places= 2)
    cxreferencia= models.TextField
    dcontabilizado = models.DateField
    cxtransaccion = models.CharField(max_length= 10)
    norden = models.SmallIntegerField


