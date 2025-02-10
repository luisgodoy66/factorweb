# from re import T
from django.db import models
from bases.models import ClaseModelo
from empresa.models import Tipos_factoring
from pais.models import Bancos
from clientes.models import Datos_generales as Datos_generales_cliente\

class Clientes(ClaseModelo):
    cxcliente = models.CharField(max_length=13)
    ctnombre =models.CharField(max_length=100)
    cxzona =models.CharField(max_length=5, null=True)
    cxlocalidad =models.CharField(max_length=4, null=True)
    # cxpais =models.ForeignKey('Pais',to_field="cxpais", on_delete=models.CASCADE)
    ctdireccion =models.TextField(null=True)
    ctemail =models.EmailField(null=True)
    ctemail2 =models.EmailField(null=True, blank=True)
    cttelefono1 =models.CharField(max_length=30,null=True, blank=True)
    cttelefono2 =models.CharField(max_length=30,null=True, blank=True)
    ctcelular =models.CharField(max_length=30,null=True, blank=True)
    ctgirocomercial =models.TextField(null=True)

    def __str__(self):
        return self.ctnombre
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cxcliente', 'empresa'], name='cliente_solicitud')
        ]
        ordering = [
            'ctnombre'
            ]  

class Asignacion(ClaseModelo):
    TIPOS_DE_ASIGNACION = (
        ('A', 'Con accesorios'),
        ('F', 'Facturas puras'),
    )
    TIPOS_DE_ESTADO = (
        ('A', 'Aceptada'),
        ('R', 'Rechazada'),
        ('P', 'Pendiente'),
        ('L', 'Liquidada'),
    )
    cxcliente=models.ForeignKey(Clientes, on_delete=models.CASCADE
        , related_name="cliente_asignacion")
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , on_delete=models.RESTRICT)
    cxtipo = models.CharField(max_length=1, choices=TIPOS_DE_ASIGNACION) 
    nvalor = models.DecimalField(max_digits=15, decimal_places =2
        , default=0) 
    ncantidaddocumentos = models.SmallIntegerField(default=0)
    cxestado = models.CharField(max_length=1, choices=TIPOS_DE_ESTADO
        , default='P')
    datencion = models.DateTimeField(null=True)
    cxusuarioatencion = models.IntegerField(null=True)
    asignacion = models.BigIntegerField(null=True)
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    lrequiereaceptacion = models.BooleanField(default=False)
    cxasignacion = models.CharField(max_length=8 , null=True) 
    dnegociacion = models.DateTimeField(auto_created=True, null=True) 
    ddesembolso= models.DateField(auto_created=True, null=True) 
    nanticipo = models.DecimalField(max_digits=10, decimal_places= 2, default=0)
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    ndescuentodecartera = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    notroscargos = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    nbaseiva = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    nbasenoiva = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    jotroscargos = models.JSONField(blank=True, null=True)
    ctinstrucciondepago = models.TextField(blank=True)
    nporcentajeiva = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    cliente=models.ForeignKey(Datos_generales_cliente, null=True, default=None
        , on_delete=models.CASCADE
    )
    def cargos(self):
        return self.ngao + self.ndescuentodecartera + self.notroscargos

    def neto(self):
        return (self.nanticipo 
                - self.ngao 
                - self.notroscargos
                - self.ndescuentodecartera 
                - self.niva)
    
    def estado(self):
        return self.get_cxestado_display()
    
    
class Documentos(ClaseModelo):
    cxasignacion=models.ForeignKey(Asignacion
        , on_delete=models.CASCADE
    )
    cxcomprador=models.CharField(max_length=13) 
    ctcomprador = models.CharField(max_length=100)
    ctserie1=models.CharField(max_length=3, null=True)
    ctserie2=models.CharField(max_length=3, null=True)
    ctdocumento = models.CharField(max_length=9) 
    demision  = models.DateField() 
    dvencimiento  = models.DateField() 
    nvalorantesiva = models.DecimalField(max_digits=10,decimal_places= 2)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    nretencioniva = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    nretencionrenta = models.DecimalField(max_digits=10,decimal_places= 2, default=0) 
    ntotal = models.DecimalField(max_digits=10,decimal_places= 2, default=0) 
    nvalornonegociado = models.DecimalField(max_digits=10,decimal_places= 2, default=0) 
    nporcentajeanticipo = models.DecimalField(max_digits=5,decimal_places= 2, default=0)
    ntasacomision = models.DecimalField(max_digits=11,decimal_places= 8, default=0)
    ntasadescuento = models.DecimalField(max_digits=11,decimal_places= 8, default=0)
    nanticipo = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ndescuentocartera = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    nplazo = models.IntegerField(default=0)
    cxautorizacion_ec = models.CharField(max_length=49, null=True)

    def total_negociado(self):
        return self.ntotal - self.nvalornonegociado

    def __str__(self):
        return self.ctdocumento

    def total_cargos(self):
        return self.ngao + self.ndescuentocartera
        
class ChequesAccesorios(ClaseModelo):
    PROPIETARIO = (
        ('C', 'Cliente'),
        ('D', 'Deudor'),
    )
    cxpropietariocuenta = models.CharField(max_length=1, choices= PROPIETARIO
        , default='D')
    documento = models.ForeignKey(Documentos
        , on_delete=models.CASCADE)
    cxbanco = models.ForeignKey(Bancos, on_delete=models.RESTRICT
        , related_name="banco_cheque_solicitud")
    ctcuenta = models.CharField(max_length=15)
    ctcheque = models.CharField(max_length=13) 
    ctgirador = models.CharField(max_length=60) 
    ntotal = models.DecimalField(max_digits= 15,decimal_places= 2, default=0) 
    dvencimiento  = models.DateField() 
    nporcentajeanticipo = models.DecimalField(max_digits=5,decimal_places= 2, default=0)
    ntasacomision = models.DecimalField(max_digits=11,decimal_places= 8, default=0)
    ntasadescuento = models.DecimalField(max_digits=11,decimal_places= 8, default=0)
    nanticipo = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ndescuentocartera = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    nplazo = models.IntegerField(default=0)

    def __str__(self):
        return '{} CTA.{} CH/{}'.format(self.cxbanco,self.ctcuenta, self.ctcheque)

class Solicitud_aceptacion(ClaseModelo):
    ESTADO = (
        ('P', 'Pendiente'),
        ('A', 'Aceptada'),
        ('R', 'Rechazada'),
    )
    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE)
    cxestado = models.CharField(max_length=1, default='P')
    dsolicitud = models.DateTimeField(auto_created=True)
    ctusuariorespuesta = models.CharField(max_length=15, null=True)
    drespuesta = models.DateTimeField(null=True)