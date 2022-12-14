from email.policy import default
from statistics import mode
from django.db import models

from bases.models import ClaseModelo
from empresa.models import Datos_participantes , Tipos_factoring, Cuentas_bancarias
from operaciones.models import Documentos, ChequesAccesorios, Cargos_detalle
from clientes import models as Cliente_models

class Cheques(ClaseModelo):
    TIPOS_DE_PARTICIPANTES = (
        ('D', 'Deudor'),
        ('C', 'Cliente'),
    )
    cxparticipante = models.ForeignKey(Datos_participantes
        ,to_field="cxparticipante", on_delete=models.CASCADE
        , related_name="cliente_cheque"
    )
    cxtipoparticipante = models.CharField(max_length=1, choices=TIPOS_DE_PARTICIPANTES) 
    cxcuentabancaria = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , on_delete = models.RESTRICT)
    ctcheque = models.CharField(max_length=8) 
    ctplaza = models.CharField(max_length=30, null=True)  
    ctgirador = models.CharField(max_length=60, blank=True) 
    cxestado = models.CharField(max_length=1, default=" ") 
    nvalor = models.DecimalField(max_digits= 10,decimal_places= 2) 
    # demision  = models.DateTimeField() 

    def __str__(self):
        return '{} CH/{}'.format(self.cxcuentabancaria, self.ctcheque)

class Documentos_cabecera(ClaseModelo):
    FORMAS_DE_PAGO = (
        ('EFE', 'Efectivo'),
        ('CHE', 'Cheque'),
        ('MOV', 'Movimiento contable'),
        ('TRA', 'Transferencia'),
        ('DEP', 'Deposito de accesorio'),
    )
    cxcobranza = models.CharField(max_length=8, )
    cxcliente=models.ForeignKey(Cliente_models.Datos_generales
        ,to_field="cxcliente", on_delete=models.CASCADE
        , related_name="cliente_cobranza"
    )
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , to_field="cxtipofactoring", on_delete=models.RESTRICT
        , related_name="tipofactoring_cobranza")
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dcobranza = models.DateTimeField(auto_created=True) 
    dliquidacion = models.DateTimeField(null=True) 
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsobrepago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cxestado = models.CharField(max_length=1, default=' ')
    cxcheque = models.ForeignKey(Cheques, on_delete=models.RESTRICT
        , null=True, related_name='cheque_cobranza')
    cxcuentatransferencia = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , null=True, on_delete = models.RESTRICT)
    cxcuentadeposito = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True, related_name="banco_deposito")
    # ctreferenciadeposito = models.CharField(max_length=15)
    ddeposito = models.DateTimeField(null=True) 
    lpagadoporelcliente = models.BooleanField(default=False)
    ldepositoencuentaconjunta = models.BooleanField(default=False)
    cxaccesorio = models.ForeignKey(ChequesAccesorios
        , on_delete = models.RESTRICT, null=True)

    def __str__(self):
        return self.cxcobranza

    def movimiento(self):
        # si est?? protestada debe decir "cobranza protestada"
        if self.cxestado=='P' :
            x = 'Cobranza protestada'
        else:
            x = 'Cobranza'
        return x

from django.contrib.auth.models import User
class Documentos_detalle(ClaseModelo):
    cxcobranza =models.ForeignKey(Documentos_cabecera
        , on_delete=models.CASCADE
    )
    cxdocumento=models.ForeignKey(Documentos
        , on_delete=models.CASCADE
    )
    nvalorcobranza = models.DecimalField(max_digits=10, decimal_places=2)
    nvalorbaja= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nretenciones= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsaldoaldia= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ndiasacondonar = models.SmallIntegerField(default=0)
    cxusuariocondona = models.ForeignKey(User, on_delete= models.CASCADE,
        related_name="usuariocondona", null= True)

    def dias_vencidos(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        if self.cxdocumento.cxasignacion.cxtipo=='P':
            vencimiento = self.cxdocumento.dvencimiento
        else:
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento

        return self.cxcobranza.dcobranza - vencimiento

    def vencimiento(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        if self.cxdocumento.cxasignacion.cxtipo=='P':
            vencimiento = self.cxdocumento.dvencimiento
        else:
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento

        return vencimiento

    def aplicado(self):
        return self.nvalorcobranza + self.nvalorbaja + self.nretenciones

class Liquidacion_cabecera(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperaci??n'),
        ('C', 'Cobranzas'),
    )
    cxcliente=models.ForeignKey(Cliente_models.Datos_generales
        ,to_field="cxcliente", on_delete=models.CASCADE
        , related_name="cliente_liquidacion"
    )
    cxliquidacion = models.CharField(max_length=8 , unique=True) 
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , to_field="cxtipofactoring", on_delete=models.RESTRICT
        , related_name="tipofactoring_liquidacioncobranzas")
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION)
    jcobranzas = models.JSONField()
    nvuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsobrepago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ngao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ngaoa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ndescuentodecartera = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nretenciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nbajas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    niva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nneto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ctinstrucciondepago = models.TextField()
    dliquidacion = models.DateTimeField()
    ddesembolso= models.DateTimeField()
    ldesembolsada = models.BooleanField(default=False)

    def __str__(self):
        return self.cxliquidacion

class Liquidacion_detalle(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperaci??n'),
        ('C', 'Cobranzas'),
        ('L', 'Liquidaci??n'),
    )
    liquidacion = models.ForeignKey(Liquidacion_cabecera
        , on_delete=models.CASCADE, related_name="liquidacion_detalle")
    cargo = models.ForeignKey(Cargos_detalle, on_delete=models.RESTRICT)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nvaloraplicado = models.DecimalField(max_digits=10, decimal_places=2
        , default=0, null=True)
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION)
    operacion = models.BigIntegerField()

from operaciones.models import Motivos_protesto_maestro

class Cheques_protestados(ClaseModelo):
    FORMAS_DE_COBRO = (
        ('CHE', 'Cheque'),
        ('DEP', 'Deposito de accesorio'),
    )

    cheque = models.ForeignKey(Cheques, on_delete= models.RESTRICT
        , related_name="cheque_protestado")
    cxformacobro = models.CharField(max_length=3, choices=FORMAS_DE_COBRO)
    dprotesto = models.DateField()
    motivoprotesto = models.ForeignKey(Motivos_protesto_maestro, on_delete=models.RESTRICT)
    nvalornotadebito = models.DecimalField(max_digits=10, decimal_places=2)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    nsaldo =  models.DecimalField(max_digits=10, decimal_places=2)
    cxestado = models.CharField(max_length=1, default="A") 
    dultimacobranza = models.DateTimeField(null=True) 
    cxtipooperacion = models.CharField(max_length=1)

    def __str__(self):
        return '{} CH/{}'.format(self.cheque.cxcuentabancaria, self.cheque.ctcheque)        

class Documentos_protestados(ClaseModelo):
    chequeprotestado = models.ForeignKey(Cheques_protestados, on_delete= models.RESTRICT)
    documento = models.ForeignKey(Documentos, on_delete=models.CASCADE)
    accesorio = models.ForeignKey(ChequesAccesorios, on_delete=models.CASCADE
        ,null=True, default=None)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2)
    nsaldo = models.DecimalField(max_digits=10, decimal_places=2)
    nvalorbajacobranza =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsaldobajacobranza =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cxestado = models.CharField(max_length=1, default="A") 
    dultimacobranza = models.DateTimeField(null=True) 

class Recuperaciones_cabecera(ClaseModelo):
    FORMAS_DE_PAGO = (
        ('EFE', 'Efectivo'),
        ('CHE', 'Cheque'),
        ('MOV', 'Movimiento contable'),
        ('TRA', 'Transferencia'),
    )
    cxrecuperacion = models.CharField(max_length=8, )
    cxcliente = models.ForeignKey(Cliente_models.Datos_generales
        ,to_field="cxcliente", on_delete=models.CASCADE
    )
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , to_field="cxtipofactoring", on_delete=models.RESTRICT)
    cxformacobro = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dcobranza = models.DateTimeField(auto_created=True) 
    dliquidacion = models.DateTimeField(null=True) 
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsobrepago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cxestado = models.CharField(max_length=1, default=' ')
    cxcheque = models.ForeignKey(Cheques, on_delete=models.RESTRICT
        , null=True, related_name='cheque_recuperacion')
    cxcuentatransferencia = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , null=True, on_delete = models.RESTRICT)
    cxcuentadeposito = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True)
    # ctreferenciadeposito = models.CharField(max_length=15)
    ddeposito = models.DateTimeField(null=True) 

    def __str__(self):
        return self.cxrecuperacion

    def movimiento(self):
        # si est?? protestada debe decir "cobranza protestada"
        if self.cxestado=='P' :
            x = 'Recuperaci??n protestada'
        else:
            x = 'Recuperaci??n'
        return x

class Recuperaciones_detalle(ClaseModelo):
    recuperacion =models.ForeignKey(Recuperaciones_cabecera
        , on_delete=models.CASCADE
    )
    documentoprotestado=models.ForeignKey(Documentos_protestados
        , on_delete=models.CASCADE
    )
    chequeprotestado = models.ForeignKey(Cheques_protestados, on_delete= models.RESTRICT)
    nsaldoaldia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nvalorrecuperacion = models.DecimalField(max_digits=10, decimal_places=2)
    nvalorbaja = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsaldoaldiabajacobranza = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nvalorbajacobranza = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ndiasacondonar = models.SmallIntegerField(default=0, null=True)
    cxusuariocondona = models.ForeignKey(User, on_delete= models.CASCADE, null= True)

    def dias_vencidos(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        if self.documentoprotestado.documento.cxasignacion.cxtipo=='P':
            vencimiento = self.documentoprotestado.documento.dvencimiento
        else:
            vencimiento = self.documentoprotestado.accesorio.dvencimiento

        return self.recuperacion.dcobranza - vencimiento

    def vencimiento(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio 
        if self.documentoprotestado.documento.cxasignacion.cxtipo=='P':
            vencimiento = self.documentoprotestado.documento.dvencimiento
        else:
            vencimiento = self.documentoprotestado.accesorio.dvencimiento

        return vencimiento

    def aplicado(self):
        return self.nvalorrecuperacion + self.nvalorbaja + self.nvalorbajacobranza
