from email.policy import default
from statistics import mode
from django.db import models
from django.contrib.auth.models import User

from bases.models import ClaseModelo
from empresa.models import Datos_participantes , Tipos_factoring, Cuentas_bancarias
from clientes import models as Cliente_models
from operaciones.models import Documentos, ChequesAccesorios\
    , Cargos_detalle as Operaciones_cargos, Motivos_protesto_maestro

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

from cuentasconjuntas import models as CuentasConjuntasModels
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
    cxestado = models.CharField(max_length=1, default='A')
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
    cxcuentaconjunta = models.ForeignKey(CuentasConjuntasModels.Cuentas_bancarias
        , on_delete=models.RESTRICT, null = True, related_name="cuenta_deposito")
    cxaccesorio = models.ForeignKey(ChequesAccesorios
        , on_delete = models.RESTRICT, null=True)

    def __str__(self):
        return self.cxcobranza

    def movimiento(self):
        # si está protestada debe decir "cobranza protestada"
        if self.cxestado=='P' :
            x = 'Cobranza protestada'
        else:
            x = 'Cobranza'
        return x

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
        if self.cxdocumento.cxasignacion.cxtipo=='F':
            vencimiento = self.cxdocumento.dvencimiento
        else:
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento

        return self.cxcobranza.dcobranza - vencimiento

    def vencimiento(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        if self.cxdocumento.cxasignacion.cxtipo=='F':
            vencimiento = self.cxdocumento.dvencimiento
        else:
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento

        return vencimiento

    def aplicado(self):
        return self.nvalorcobranza + self.nvalorbaja + self.nretenciones

class Liquidacion_cabecera(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperación'),
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
    cxestado = models.CharField(max_length=1, default='A')

    def __str__(self):
        return self.cxliquidacion

class Liquidacion_detalle(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperación'),
        ('C', 'Cobranzas'),
        ('L', 'Liquidación'),
        ('D', 'Debito bancario'),
    )
    liquidacion = models.ForeignKey(Liquidacion_cabecera
        , on_delete=models.CASCADE, related_name="liquidacion_detalle")
    cargo = models.ForeignKey(Operaciones_cargos, on_delete=models.RESTRICT)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nvaloraplicado = models.DecimalField(max_digits=10, decimal_places=2
        , default=0, null=True)
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION)
    operacion = models.BigIntegerField()

from operaciones.models import  Notas_debito_cabecera

class Cheques_protestados(ClaseModelo):
    FORMAS_DE_COBRO = (
        ('CHE', 'Cheque'),
        ('DEP', 'Deposito de accesorio'),
    )

    cheque = models.ForeignKey(Cheques, on_delete= models.RESTRICT
        , related_name="cheque_protestado")
    cxformacobro = models.CharField(max_length=3, choices=FORMAS_DE_COBRO)
    dprotesto = models.DateField()
    motivoprotesto = models.ForeignKey(Motivos_protesto_maestro
        , on_delete=models.RESTRICT)
    # nvalornotadebito = models.DecimalField(max_digits=10, decimal_places=2)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    nsaldo =  models.DecimalField(max_digits=10, decimal_places=2)
    cxestado = models.CharField(max_length=1, default="A") 
    dultimacobranza = models.DateTimeField(null=True) 
    cxtipooperacion = models.CharField(max_length=1)
    notadedebito = models.ForeignKey(Notas_debito_cabecera, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{} CH/{}'.format(self.cheque.cxcuentabancaria, self.cheque.ctcheque)        

class Documentos_protestados(ClaseModelo):
    chequeprotestado = models.ForeignKey(Cheques_protestados, on_delete= models.RESTRICT)
    documento = models.ForeignKey(Documentos, on_delete=models.CASCADE)
    accesorio = models.ForeignKey(ChequesAccesorios, on_delete=models.CASCADE
        ,null=True, default=None)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2)
    nsaldo = models.DecimalField(max_digits=10, decimal_places=2)
    nvalorbajacobranza =  models.DecimalField(max_digits=10, decimal_places=2
        , default=0)
    nsaldobajacobranza =  models.DecimalField(max_digits=10, decimal_places=2
        , default=0)
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
    cxestado = models.CharField(max_length=1, default='A')
    cxcheque = models.ForeignKey(Cheques, on_delete=models.RESTRICT
        , null=True, related_name='cheque_recuperacion')
    cxcuentatransferencia = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , null=True, on_delete = models.RESTRICT)
    cxcuentadeposito = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True)
    # ctreferenciadeposito = models.CharField(max_length=15)
    ddeposito = models.DateTimeField(null=True) 
    lpagadoporelcliente = models.BooleanField(default=False)
    ldepositoencuentaconjunta = models.BooleanField(default=False)
    cxcuentaconjunta = models.ForeignKey(CuentasConjuntasModels.Cuentas_bancarias
        , on_delete=models.RESTRICT, null = True, related_name="cuentaconjunta_deposito")

    def __str__(self):
        return self.cxrecuperacion

    def movimiento(self):
        # si está protestada debe decir "cobranza protestada"
        if self.cxestado=='P' :
            x = 'Recuperación protestada'
        else:
            x = 'Recuperación'
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
        if self.documentoprotestado.documento.cxasignacion.cxtipo=='F':
            vencimiento = self.documentoprotestado.documento.dvencimiento
        else:
            vencimiento = self.documentoprotestado.accesorio.dvencimiento

        return self.recuperacion.dcobranza - vencimiento

    def vencimiento(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio 
        if self.documentoprotestado.documento.cxasignacion.cxtipo=='F':
            vencimiento = self.documentoprotestado.documento.dvencimiento
        else:
            vencimiento = self.documentoprotestado.accesorio.dvencimiento

        return vencimiento

    def aplicado(self):
        return self.nvalorrecuperacion + self.nvalorbaja + self.nvalorbajacobranza

class Cargos_cabecera(ClaseModelo):
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
        , related_name="cliente_cobranza_cargos"
    )
    cxtipofactoring = models.ForeignKey(Tipos_factoring, null=True
        , to_field="cxtipofactoring", on_delete=models.RESTRICT
        , related_name="tipofactoring_cobranza_cargos")
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dcobranza = models.DateTimeField(auto_created=True) 
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsobrepago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cxestado = models.CharField(max_length=1, default=' ')
    cxcheque = models.ForeignKey(Cheques, on_delete=models.RESTRICT
        , null=True, related_name='cheque_cobranza_cargos')
    cxcuentatransferencia = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , null=True, on_delete = models.RESTRICT)
    cxcuentadeposito = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True, related_name="banco_deposito_cargos")
    # ctreferenciadeposito = models.CharField(max_length=15)
    ddeposito = models.DateTimeField(null=True) 

    def __str__(self):
        return self.cxcobranza

    def movimiento(self):
        # si está protestada debe decir "cobranza ... protestada"
        if self.cxestado=='P' :
            x = 'Cobranza de cargos protestada'
        else:
            x = 'Cobranza de cargos'
        return x

class Cargos_detalle(ClaseModelo):
    cxcobranza =models.ForeignKey(Cargos_cabecera, on_delete=models.CASCADE)
    notadedebito = models.ForeignKey(Notas_debito_cabecera, on_delete=models.CASCADE)
    nsaldoaldia= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nvalorcobranza = models.DecimalField(max_digits=10, decimal_places=2)
    jcargos = models.JSONField()

class DebitosCuentasConjuntas(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperación'),
        ('C', 'Cobranzas'),
    )
    cuentabancaria = models.ForeignKey(CuentasConjuntasModels.Cuentas_bancarias
        , on_delete=models.CASCADE)
    dmovimiento = models.DateField()
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ctmotivo = models.CharField(max_length=60)
    notadedebito = models.OneToOneField(Notas_debito_cabecera, on_delete=models.CASCADE)
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION
        , null=True)
    # cobranza = models.OneToOneField(Documentos_cabecera, on_delete=models.CASCADE
    #     , null=True)
    operacion = models.BigIntegerField(null=True)

    def cobranza(self):
        if self.cxtipooperacion=='C':
            x = Documentos_cabecera.objects.filter(pk = self.operacion).first()
            return x.cxcobranza
        elif self.cxtipooperacion=='R':
            x = Recuperaciones_cabecera.objects.filter(pk = self.operacion).first()
            return x.cxrecuperacion
        else:
            return ''