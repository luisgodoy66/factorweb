# from email.policy import default
# from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Value, DecimalField\
    , ExpressionWrapper, IntegerField, CharField, DateField, F\
    , Case, When
from django.db.models.functions import TruncDay, Cast\
    , ExtractDay, Concat, Floor, Mod, Ceil

from datetime import timedelta, datetime, date

from bases.models import ClaseModelo
from empresa.models import Datos_participantes , Tipos_factoring\
    , Cuentas_bancarias, Tasas_factoring
from clientes import models as Cliente_models
from operaciones.models import Documentos, ChequesAccesorios\
    , Cargos_detalle as Operaciones_cargos, Motivos_protesto_maestro\
    , Pagare_detalle as Cuotas, Cortes_historico\
    , Revision_cartera_detalle, Asignacion
from cuentasconjuntas import models as CuentasConjuntasModels
from api.models import Configuracion_twilio_whatsapp

import decimal
class Cheques(ClaseModelo):
    TIPOS_DE_PARTICIPANTES = (
        ('D', 'Deudor'),
        ('C', 'Cliente'),
    )
    cxparticipante = models.ForeignKey(Datos_participantes
        , on_delete=models.CASCADE
        , related_name="cliente_cheque"
    )
    cxtipoparticipante = models.CharField(max_length=1, choices=TIPOS_DE_PARTICIPANTES) 
    cxcuentabancaria = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , on_delete = models.RESTRICT)
    ctcheque = models.CharField(max_length=8) 
    ctplaza = models.CharField(max_length=30, null=True)  
    ctgirador = models.CharField(max_length=60, blank=True) 
    cxestado = models.CharField(max_length=1, default="A") 
    nvalor = models.DecimalField(max_digits= 10,decimal_places= 2) 
    # demision  = models.DateTimeField() 

    def __str__(self):
        return '{} CH/{}'.format(self.cxcuentabancaria, self.ctcheque)

from contabilidad.models import Diario_cabecera

class Documentos_cabecera_Manager(models.Manager):
    def valores_cobrados_por_dia(self, id_empresa, año, mes):
        return self.filter(
            empresa = id_empresa,
            leliminado=False,
            dcobranza__year=año,
            dcobranza__month=mes,
            cxestado__in=('A','L')  # sólo se consideran las activas y las liquidadas
        ).annotate(
            dia=TruncDay('dcobranza')
        ).values('dia').annotate(
            total_valor=Sum('nvalor')
        ).order_by('dia')

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
        , on_delete=models.CASCADE
        , related_name="cliente_cobranza"
    )
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , on_delete=models.RESTRICT, related_name="tipofactoring_cobranza")
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dcobranza = models.DateField(auto_created=True) 
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
    lcontabilizada = models.BooleanField(default=False, null=True)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_cobranza"
                                     , null=True)

    objects = Documentos_cabecera_Manager()
    
    def __str__(self):
        return self.cxcobranza

    def movimiento(self):
        # si está protestada debe decir "cobranza protestada"
        if self.cxestado=='P' :
            x = 'Cobranza protestada'
        else:
            x = 'Cobranza'
        return x
    
    def estado(self):
        return self.get_cxestado_display()
    
class Documentos_detalle_Manager(models.Manager):
    def promedio_ponderado_demora(self, id_cliente):
        # promedio ponderado de demora de los documentos
        # de la empresa
        documentos = self.filter(leliminado=False
                                 , cxcobranza__cxcliente=id_cliente
                                 )
        
        total = documentos.aggregate(
            Total=Sum(
                models.F('nvalorcobranza') 
                + models.F('nvalorbaja') 
                + models.F('nretenciones')
                )
            )
        
        totaldias = 0
        for documento in documentos:
            dias_vencidos = decimal.Decimal( documento.dias_vencidos_vencimiento_original())
            totaldias += dias_vencidos * (
                documento.nvalorcobranza 
                + documento.nvalorbaja 
                + documento.nretenciones)
        
        if total['Total'] and totaldias:
            return totaldias / total['Total']
        else:
            return 0

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
    accesorioquitado = models.ForeignKey(ChequesAccesorios, on_delete=models.RESTRICT
                                        , null=True)

    objects = Documentos_detalle_Manager()

    def dias_vencidos(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        if self.cxdocumento.cxasignacion.cxtipo=='F':
            vencimiento = self.cxdocumento.dvencimiento
            if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
                vencimiento = vencimiento + timedelta(self.cxdocumento.ndiasprorroga)
        elif self.cxcobranza.cxformapago =='DEP':
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento
            if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
                vencimiento = vencimiento + timedelta(self.cxcobranza.cxaccesorio.ndiasprorroga)
        else:
            vencimiento = self.accesorioquitado.dvencimiento
            if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
                vencimiento = vencimiento + timedelta(self.accesorioquitado.ndiasprorroga)

        return (self.cxcobranza.dcobranza - vencimiento)/timedelta(days=1)

    def dias_vencidos_vencimiento_original(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        # usado en cálculo de promedio ponderado de demora
        if self.cxdocumento.cxasignacion.cxtipo=='F':
            vencimiento = self.cxdocumento.dvencimiento
            # if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
            #     vencimiento = vencimiento + timedelta(self.cxdocumento.ndiasprorroga)
        elif self.cxcobranza.cxformapago =='DEP':
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento
            # if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
            #     vencimiento = vencimiento + timedelta(self.cxcobranza.cxaccesorio.ndiasprorroga)
        else:
            vencimiento = self.accesorioquitado.dvencimiento
            # if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
            #     vencimiento = vencimiento + timedelta(self.accesorioquitado.ndiasprorroga)

        return (self.cxcobranza.dcobranza - vencimiento)/timedelta(days=1)

    def vencimiento(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio grabado en la cabecera
        if self.cxdocumento.cxasignacion.cxtipo=='F':
            vencimiento = self.cxdocumento.dvencimiento
            if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
                vencimiento = vencimiento + timedelta(self.cxdocumento.ndiasprorroga)
        elif self.cxcobranza.cxformapago =='DEP':
            vencimiento = self.cxcobranza.cxaccesorio.dvencimiento
            if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
                vencimiento = vencimiento + timedelta(self.cxcobranza.cxaccesorio.ndiasprorroga)
        else:
            vencimiento = self.accesorioquitado.dvencimiento
            if self.cxcobranza.cxtipofactoring.lanticipatotalnegociado:
                vencimiento = vencimiento + timedelta(self.accesorioquitado.ndiasprorroga)

        return vencimiento

    def aplicado(self):
        if self.cxcobranza.cxestado =='E' or self.cxcobranza.cxestado =='P':
            return 0
        else:
            return self.nvalorcobranza + self.nvalorbaja + self.nretenciones

    def retencionesybajas(self):
        return self.nvalorbaja + self.nretenciones

    def demoradepago(self):
        return (self.cxcobranza.dcobranza - self.vencimiento())/timedelta(days=1)
    
class Liquidacion_cabecera(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperación'),
        ('C', 'Cobranzas'),
    )
    cxcliente=models.ForeignKey(Cliente_models.Datos_generales
        , on_delete=models.CASCADE
        , related_name="cliente_liquidacion"
    )
    cxliquidacion = models.CharField(max_length=8 ) 
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , on_delete=models.RESTRICT
        , related_name="tipofactoring_liquidacioncobranzas")
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION)
    jcobranzas = models.JSONField()
    nvuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsobrepago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ngao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ngaoa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ndescuentodecartera = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ndescuentodecarteravencido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nretenciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nbajas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notroscargos = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    nbaseiva = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    nbasenoiva = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    niva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jotroscargos = models.JSONField(blank=True, null=True)
    nneto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ctinstrucciondepago = models.TextField()
    dliquidacion = models.DateTimeField()
    ddesembolso= models.DateTimeField()
    ldesembolsada = models.BooleanField(default=False)
    cxestado = models.CharField(max_length=1, default='A')
    lfacturagenerada = models.BooleanField(default=False)
    nporcentajeiva = models.DecimalField(max_digits=5, decimal_places=2, default=12)

    def __str__(self):
        return self.cxliquidacion

    def cargos(self):
        return (self.ngao 
                + self.ngaoa
                + self.ndescuentodecartera 
                + self.ndescuentodecarteravencido
                + self.nretenciones
                + self.nbajas
                + self.notros
                + self.notroscargos)

    def facturar(self):
        return (self.ngao 
                + self.ngaoa
                + self.ndescuentodecartera 
                + self.ndescuentodecarteravencido
                + self.notroscargos)

    def neto(self):
        return (self.nvuelto
                + self.nsobrepago 
                - self.cargos()
                - self.niva)

    def otros_cargos(self):
        return self.notroscargos + self.notros
        
class Liquidacion_detalle(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('R', 'Recuperación'),
        ('C', 'Cobranzas'),
        ('L', 'Liquidación'),
        ('D', 'Debito bancario'),
        ('F', 'Factura'),
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

class Protestos_Manager(models.Manager):
    def TotalProtestos(self, id_empresa):
        return self.filter(leliminado=False
                           , empresa = id_empresa
                           , nsaldocartera__gt = 0)\
            .aggregate(Total = Sum('nsaldocartera'))

    def protestos_pendientes(self, id_empresa):
        cp = self.filter(nsaldocartera__gt=0
                         , leliminado = False
                         , empresa = id_empresa
                         , cxtipooperacion='C')\
            .values('id','cheque__cheque_cobranza'
                    ,'cheque__cheque_cobranza__cxcliente__cxcliente__ctnombre'
                    ,'cheque__cheque_cobranza__cxcobranza'
                    ,'cheque__cheque_cobranza__dcobranza'
                    ,'cheque__cheque_cobranza__ddeposito'
                    ,'cheque__ctgirador','dprotesto'
                    ,'motivoprotesto__ctmotivoprotesto'
                    ,'nvalor','nsaldocartera','nvalorcartera', 'cheque__cxparticipante'
                    )
        rp = self.filter(nsaldocartera__gt=0
                         , leliminado = False
                         , empresa = id_empresa
                         , cxtipooperacion='R')\
            .values('id','cheque__cheque_recuperacion'
                    ,'cheque__cheque_recuperacion__cxcliente__cxcliente__ctnombre'
                    ,'cheque__cheque_recuperacion__cxrecuperacion'
                    ,'cheque__cheque_recuperacion__dcobranza'
                    ,'cheque__cheque_recuperacion__ddeposito'
                    ,'cheque__ctgirador','dprotesto'
                    ,'motivoprotesto__ctmotivoprotesto'
                    ,'nvalor','nsaldocartera','nvalorcartera', 'cheque__cxparticipante'
                    )
        return cp.union(rp)
        
    def protestos_pendientes_cliente(self, id_empresa, id_cliente):
        cp = self.filter(nsaldocartera__gt=0
                         , leliminado = False
                         , empresa = id_empresa
                         , cheque__cheque_cobranza__cxcliente = id_cliente
                         , cxtipooperacion='C')\
            .values('id','cheque__cheque_cobranza'
                    ,'cheque__cheque_cobranza__cxcliente__cxcliente__ctnombre'
                    ,'cheque__cheque_cobranza__cxcobranza'
                    ,'cheque__cheque_cobranza__dcobranza'
                    ,'cheque__cheque_cobranza__ddeposito'
                    ,'cheque__ctgirador','dprotesto'
                    ,'motivoprotesto__ctmotivoprotesto'
                    ,'nvalor','nsaldocartera','nvalorcartera'
                    )
        rp = self.filter(nsaldocartera__gt=0
                         , leliminado = False
                         , empresa = id_empresa
                         , cheque__cheque_recuperacion__cxcliente = id_cliente
                         , cxtipooperacion='R')\
            .values('id','cheque__cheque_recuperacion'
                    ,'cheque__cheque_recuperacion__cxcliente__cxcliente__ctnombre'
                    ,'cheque__cheque_recuperacion__cxrecuperacion'
                    ,'cheque__cheque_recuperacion__dcobranza'
                    ,'cheque__cheque_recuperacion__ddeposito'
                    ,'cheque__ctgirador','dprotesto'
                    ,'motivoprotesto__ctmotivoprotesto'
                    ,'nvalor','nsaldocartera','nvalorcartera'
                    )
        return cp.union(rp)
        
    def TotalProtestosCliente(self, id_cliente):
        return self.filter(leliminado=False
                           , nsaldocartera__gt = 0)\
                    .filter(Q(cheque__cheque_cobranza__cxcliente = id_cliente
                              , cxtipooperacion='C')
                            |Q(cheque__cheque_recuperacion__cxcliente = id_cliente
                               , cxtipooperacion='R'))\
            .aggregate(Total = Sum('nsaldocartera'))

class Cheques_protestados(ClaseModelo):
    FORMAS_DE_COBRO = (
        ('CHE', 'Cheque'),
        ('DEP', 'Deposito de accesorio'),
    )
    TIPO_OPERACION = (
        ("C", "Cobranza"),
        ("R","Recuperacion"),
    )
    cheque = models.ForeignKey(Cheques, on_delete= models.RESTRICT
        , related_name="cheque_protestado")
    cxformacobro = models.CharField(max_length=3, choices=FORMAS_DE_COBRO)
    dprotesto = models.DateField()
    motivoprotesto = models.ForeignKey(Motivos_protesto_maestro
        , on_delete=models.RESTRICT)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    nvalorcartera = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsaldocartera =  models.DecimalField(max_digits=10, decimal_places=2)
    cxestado = models.CharField(max_length=1, default="A") 
    dultimacobranza = models.DateTimeField(null=True) 
    cxtipooperacion = models.CharField(max_length=1, choices=TIPO_OPERACION)
    notadedebito = models.ForeignKey(Notas_debito_cabecera, on_delete=models.CASCADE, null=True)
    lcontabilizada = models.BooleanField(default=False)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_protesto"
                                     , null=True)

    objects = Protestos_Manager()

    def __str__(self):
        return '{} CH/{}'.format(self.cheque.cxcuentabancaria, self.cheque.ctcheque)        

class Documentos_protestados_Manager(models.Manager):

    def antigüedad_cartera(self, id_empresa, id_cliente=None):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        if id_cliente:
            protestados = self.filter( leliminado = False
                                      , nsaldo__gt = 0
                                      , empresa = id_empresa
                                      , documento__cxcliente = id_cliente)\
                .aggregate(
                    fvencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90
                                    , accesorio__isnull = True) ) 
                    , avencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo90
                                    , accesorio__isnull = False) ) 
                    , fvencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                    , documento__dvencimiento__gte = vcdo90
                                    , accesorio__isnull = True) ) 
                    , avencido_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo60
                                    , accesorio__dvencimiento__gte = vcdo90
                                    , accesorio__isnull = False) ) 
                    , fvencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                    , documento__dvencimiento__gte = vcdo60
                                    , accesorio__isnull = True) ) 
                    , avencido_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo30
                                    , accesorio__dvencimiento__gte = vcdo60
                                    , accesorio__isnull = False) ) 
                    , fvencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                    , documento__dvencimiento__gte = vcdo30
                                    , accesorio__isnull = True) ) 
                    , avencido_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = datetime.today()
                                    , accesorio__dvencimiento__gte = vcdo30
                                    , accesorio__isnull = False) ) 
                    ,fporvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                    , documento__dvencimiento__lte = xver30
                                    , accesorio__isnull = True) ) 
                    ,aporvencer_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gte = datetime.today()
                                    , accesorio__dvencimiento__lte = xver30
                                    , accesorio__isnull = False ) )
                    ,fporvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                    , documento__dvencimiento__lte = xver60
                                    , accesorio__isnull = True) ) 
                    ,aporvencer_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver30
                                    , accesorio__dvencimiento__lte = xver60
                                    , accesorio__isnull = False) ) 
                    ,fporvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                    , documento__dvencimiento__lte = xver90
                                    , accesorio__isnull = True) ) 
                    ,aporvencer_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver60
                                    , accesorio__dvencimiento__lte = xver90
                                    , accesorio__isnull = False) ) 
                    , fporvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90
                                    , accesorio__isnull = True)) 
                    , aporvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver90
                                    , accesorio__isnull = False)) 
                    )
        else:
            protestados = self.filter( leliminado = False
                                      , nsaldo__gt = 0
                                      , empresa = id_empresa)\
                .aggregate(
                    fvencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90
                                    , accesorio__isnull = True) ) 
                    , avencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo90
                                    , accesorio__isnull = False) ) 
                    , fvencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                    , documento__dvencimiento__gte = vcdo90
                                    , accesorio__isnull = True) ) 
                    , avencido_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo60
                                    , accesorio__dvencimiento__gte = vcdo90
                                    , accesorio__isnull = False) ) 
                    , fvencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                    , documento__dvencimiento__gte = vcdo60
                                    , accesorio__isnull = True) ) 
                    , avencido_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo30
                                    , accesorio__dvencimiento__gte = vcdo60
                                    , accesorio__isnull = False) ) 
                    , fvencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                    , documento__dvencimiento__gte = vcdo30
                                    , accesorio__isnull = True) ) 
                    , avencido_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = datetime.today()
                                    , accesorio__dvencimiento__gte = vcdo30
                                    , accesorio__isnull = False) ) 
                    ,fporvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                    , documento__dvencimiento__lte = xver30
                                    , accesorio__isnull = True) ) 
                    ,aporvencer_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gte = datetime.today()
                                    , accesorio__dvencimiento__lte = xver30
                                    , accesorio__isnull = False ) )
                    ,fporvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                    , documento__dvencimiento__lte = xver60
                                    , accesorio__isnull = True) ) 
                    ,aporvencer_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver30
                                    , accesorio__dvencimiento__lte = xver60
                                    , accesorio__isnull = False) ) 
                    ,fporvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                    , documento__dvencimiento__lte = xver90
                                    , accesorio__isnull = True) ) 
                    ,aporvencer_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver60
                                    , accesorio__dvencimiento__lte = xver90
                                    , accesorio__isnull = False) ) 
                    , fporvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90
                                    , accesorio__isnull = True)) 
                    , aporvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver90
                                    , accesorio__isnull = False)) 
                    )
        fvm90 = protestados["fvencido_mas_90"] or 0
        fv90 = protestados["fvencido_90"] or 0
        fv60 = protestados["fvencido_60"] or 0
        fv30 = protestados["fvencido_30"] or 0
        fx30 = protestados["fporvencer_30"] or 0
        fx60 = protestados["fporvencer_60"] or 0
        fx90 = protestados["fporvencer_90"] or 0
        fxm90 = protestados["fporvencer_mas_90"] or 0
        avm90=protestados["avencido_mas_90"] or 0
        av90=protestados["avencido_90"] or 0
        av60=protestados["avencido_60"] or 0
        av30=protestados["avencido_30"] or 0
        ax30=protestados["aporvencer_30"] or 0
        ax60=protestados["aporvencer_60"] or 0
        ax90=protestados["aporvencer_90"] or 0
        axm90=protestados["aporvencer_mas_90"] or 0

        protestos={}

        protestos["pvencido_mas_90"] = fvm90+avm90
        protestos["pvencido_90"] = fv90+av90
        protestos["pvencido_60"] = fv60+av60
        protestos["pvencido_30"] = fv30+av30
        protestos["pporvencer_30"] = fx30+ax30
        protestos["pporvencer_60"] = fx60+ax60
        protestos["pporvencer_90"] = fx90+ax90
        protestos["pporvencer_mas_90"] = fxm90+axm90

        return protestos
    
    def antigüedad_por_cliente_facturas(self, id_empresa):
        # la fecha de vencimiento está en el documento
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                           , nsaldo__gt = 0
                           , accesorio__isnull = True
                           , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90) ) 
                , vencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                , documento__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                , documento__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                , documento__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                , documento__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                , documento__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90))
                , total = Sum('nsaldo')
                )\
            .order_by()
    
    def antigüedad_por_cliente_accesorios(self, id_empresa):
        # la fecha de vencimiento está en el accesorio
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                           , nsaldo__gt = 0
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo60
                                , accesorio__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo30
                                , accesorio__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = datetime.today()
                                , accesorio__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gte = datetime.today()
                                , accesorio__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver30
                                , accesorio__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver60
                                , accesorio__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver90))
                , total = Sum('nsaldo')
                )\
            .order_by()
    
    def revision_cartera(self, id_empresa):

        qs = self.filter(leliminado=False
                         , nsaldo__gt=0
                         , empresa=id_empresa) 
        # Agrupar los registros por cliente y obtener los datos requeridos
        clientes= qs.values('documento__cxcliente').distinct()
        registros = {}

        for cliente in clientes:
            registros = qs.filter(documento__cxcliente=cliente['documento__cxcliente'])\
                .values(
                    'documento__cxcliente',
                ).annotate(
                    deudor=F('chequeprotestado__cheque__cxparticipante__ctnombre'),
                    documento_negociado=F('documento__ctdocumento'),
                    vencimiento_str=Cast('chequeprotestado__dprotesto', output_field=CharField()),
                    saldo=Cast('nsaldo', output_field=CharField())
            )
        registros_serializables = list(registros)

        return qs.values('documento__cxcliente__cxcliente__ctnombre',
                    'documento__cxcliente__linea_factoring__nvalor',
                    'documento__cxcliente__datos_operativos__cxclase__cxclase',
                    'documento__cxcliente__datos_operativos__cxestado',
                    'documento__cxcliente',
                    ) \
            .annotate(
                vencido_mas_60=Value(0, output_field=DecimalField()),
                vencido_mas_90=Value(0, output_field=DecimalField()),
                vencido_90=Value(0, output_field=DecimalField()),
                vencido_60=Value(0, output_field=DecimalField()),
                vencido_30=Value(0, output_field=DecimalField()),
                por_vencer=Value(0, output_field=DecimalField()),
                ptotesto=Sum('nsaldo'),
                total=Sum('nsaldo'),
                datos_json=Value(registros_serializables, output_field=models.JSONField())
            ) \
            .order_by()

    def antigüedad_por_deudor_facturas(self, id_empresa, id_cliente):
        # la fecha de vencimiento está en el documento
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                           , nsaldo__gt = 0
                           , accesorio__isnull = True
                           , empresa = id_empresa
                           , documento__cxcliente = id_cliente)\
            .values('documento__cxcomprador__cxcomprador__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90) ) 
                , vencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                , documento__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                , documento__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                , documento__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                , documento__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                , documento__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90))
                , total = Sum('nsaldo')
                )\
            .order_by()
    
    def antigüedad_por_deudor_accesorios(self, id_empresa, id_cliente):
        # la fecha de vencimiento está en el accesorio
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                           , nsaldo__gt = 0
                           , accesorio__isnull = False
                           , empresa = id_empresa
                           , documento__cxcliente = id_cliente)\
            .values('documento__cxcomprador__cxcomprador__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo60
                                , accesorio__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo30
                                , accesorio__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = datetime.today()
                                , accesorio__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gte = datetime.today()
                                , accesorio__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver30
                                , accesorio__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver60
                                , accesorio__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver90))
                , total = Sum('nsaldo')
                )\
            .order_by()
    
    def facturas_pendiente(self, id_empresa):

        cp = self.filter(leliminado=False
                           , nsaldo__gt = 0
                           , accesorio__isnull = True
                           , empresa = id_empresa)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "documento__dvencimiento"
                        , "documento__ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                    ) \
                .annotate(saldo = F('nsaldo'),
                    vencimiento =ExpressionWrapper( F('documento__dvencimiento') + F('documento__ndiasprorroga')
                                                         , output_field = DateField() ),
                    dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('documento__dvencimiento')
                                                                        , output_field=DateField())), IntegerField()),
                    dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('documento__dvencimiento')
                                                                      -F('documento__cxasignacion__ddesembolso')
                                                                      , output_field=DateField()))
                                            , IntegerField()),
                    descripcion = Concat('documento__cxasignacion__cxasignacion'
                                        , Value('-') 
                                        , ('documento__ctdocumento'), output_field=CharField())
            ) 
        rp = self.filter(leliminado=False
                           , nsaldo__gt = 0
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "accesorio__dvencimiento"
                        , "accesorio__ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                    ) \
                .annotate(
                    saldo = F('nsaldo'),
                    vencimiento =ExpressionWrapper( F('accesorio__dvencimiento') + F('accesorio__ndiasprorroga')
                                                         , output_field = DateField() ),
                    dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('accesorio__dvencimiento')
                                                                        , output_field=DateField())), IntegerField()),
                    dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('accesorio__dvencimiento')
                                                                      -F('documento__cxasignacion__ddesembolso')
                                                                        , output_field=DateField()))
                                            , IntegerField()),
                    descripcion = Concat('documento__cxasignacion__cxasignacion'
                                        , Value('-') 
                                        , ('documento__ctdocumento'), output_field=CharField())
            ) 


        return cp.union(rp).order_by('documento__cxcliente__cxcliente__ctnombre')

    def facturas_pendiente_cliente(self, id_empresa, arr_clientes):

        cp = self.filter(leliminado=False
                         , documento__cxcliente__in=arr_clientes
                           , nsaldo__gt = 0
                           , accesorio__isnull = True
                           , empresa = id_empresa)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "documento__dvencimiento"
                        , "documento__ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                    ) \
                .annotate(saldo = F('nsaldo'),
                    vencimiento =ExpressionWrapper( F('documento__dvencimiento') + F('documento__ndiasprorroga')
                                                         , output_field = DateField() ),
                    dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('documento__dvencimiento')
                                                                        , output_field=DateField())), IntegerField()),
                    dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('documento__dvencimiento')
                                                                      -F('documento__cxasignacion__ddesembolso')
                                                                      , output_field=DateField()))
                                            , IntegerField()),
                    descripcion = Concat('documento__cxasignacion__cxasignacion'
                                        , Value('-') 
                                        , ('documento__ctdocumento'), output_field=CharField())
            ) 
        rp = self.filter(leliminado=False
                           , documento__cxcliente__in=arr_clientes
                           , nsaldo__gt = 0
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "accesorio__dvencimiento"
                        , "accesorio__ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                    ) \
                .annotate(
                    saldo = F('nsaldo'),
                    vencimiento =ExpressionWrapper( F('accesorio__dvencimiento') + F('accesorio__ndiasprorroga')
                                                         , output_field = DateField() ),
                    dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('accesorio__dvencimiento')
                                                                        , output_field=DateField())), IntegerField()),
                    dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('accesorio__dvencimiento')
                                                                      -F('documento__cxasignacion__ddesembolso')
                                                                        , output_field=DateField()))
                                            , IntegerField()),
                    descripcion = Concat('documento__cxasignacion__cxasignacion'
                                        , Value('-') 
                                        , ('documento__ctdocumento'), output_field=CharField())
            ) 


        return cp.union(rp).order_by('documento__cxcliente__cxcliente__ctnombre')

    def facturas_pendiente_deudor(self, id_empresa, arr_deudores):

        cp = self.filter(leliminado=False
                         , documento__cxcomprador__in=arr_deudores
                           , nsaldo__gt = 0
                           , accesorio__isnull = True
                           , empresa = id_empresa)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "documento__dvencimiento"
                        , "documento__ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                    ) \
                .annotate(saldo = F('nsaldo'),
                    vencimiento =ExpressionWrapper( F('documento__dvencimiento') + F('documento__ndiasprorroga')
                                                         , output_field = DateField() ),
                    dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('documento__dvencimiento')
                                                                        , output_field=DateField())), IntegerField()),
                    dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('documento__dvencimiento')
                                                                      -F('documento__cxasignacion__ddesembolso')
                                                                      , output_field=DateField()))
                                            , IntegerField()),
                    descripcion = Concat('documento__cxasignacion__cxasignacion'
                                        , Value('-') 
                                        , ('documento__ctdocumento'), output_field=CharField())
            ) 
        rp = self.filter(leliminado=False
                           , documento__cxcomprador__in=arr_deudores
                           , nsaldo__gt = 0
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "accesorio__dvencimiento"
                        , "accesorio__ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                    ) \
                .annotate(
                    saldo = F('nsaldo'),
                    vencimiento =ExpressionWrapper( F('accesorio__dvencimiento') + F('accesorio__ndiasprorroga')
                                                         , output_field = DateField() ),
                    dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('accesorio__dvencimiento')
                                                                        , output_field=DateField())), IntegerField()),
                    dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('accesorio__dvencimiento')
                                                                      -F('documento__cxasignacion__ddesembolso')
                                                                        , output_field=DateField()))
                                            , IntegerField()),
                    descripcion = Concat('documento__cxasignacion__cxasignacion'
                                        , Value('-') 
                                        , ('documento__ctdocumento'), output_field=CharField())
            ) 


        return cp.union(rp).order_by('documento__cxcomprador__cxcomprador__ctnombre')

    def provision_cargos_facturas(self, id_empresa, fecha_corte, arr_clientes = None):
        gao = Tasas_factoring.objects\
            .filter(cxtasa="GAO", empresa=id_empresa).first()
        dc = Tasas_factoring.objects\
            .filter(cxtasa='DCAR', empresa=id_empresa).first()
        gaoa = Tasas_factoring.objects\
            .filter(cxtasa="GAOA", empresa=id_empresa).first()

        if not arr_clientes:
            qs = self.filter(leliminado=False
                            , nsaldo__gt = 0
                            , documento__dvencimiento__lte=fecha_corte
                            , accesorio__isnull = True
                            , empresa = id_empresa)\
                .values("documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__cxasignacion__cxtipofactoring__cttipofactoring"
                        , "documento__ctdocumento"
                        , "documento__cxasignacion__ddesembolso"
                        , "documento__cxcliente__datos_operativos__ntasamora"
                        , "documento__dvencimiento"
                    ) 
            
        else:
            qs = self.filter(leliminado=False
                            , nsaldo__gt = 0
                            , documento__cxcliente__in=arr_clientes
                            , documento__dvencimiento__lte=fecha_corte
                            , accesorio__isnull = True
                            , empresa = id_empresa)\
                .values("documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__cxasignacion__cxtipofactoring__cttipofactoring"
                        , "documento__ctdocumento"
                        , "documento__cxasignacion__ddesembolso"
                        , "documento__cxcliente__datos_operativos__ntasamora"
                        , "documento__dvencimiento"
                    ) 

        # Expresiones a usar en la anotación
        dias_negociados_expr = Cast(
            ExtractDay(
            ExpressionWrapper(
                F('documento__dvencimiento') - F('documento__cxasignacion__ddesembolso'),
                output_field=DateField()
            )
            ),
            IntegerField()
        )
        dias_vencidos_expr = Cast(
            ExtractDay(
            ExpressionWrapper(
                fecha_corte - F('documento__dvencimiento'),
                output_field=DateField()
            )
            ),
            DecimalField(max_digits=6, decimal_places=2)
        )
        saldo_anticipado_expr = ExpressionWrapper(
            F('nsaldo') * F('documento__nporcentajeanticipo') / 100,
            output_field=DecimalField()
        )

        # Anotación para dc negociado y vencido
        factor_calcular_expr = Case(
            When(documento__cxtipofactoring__lgeneradcenaceptacion=True, then=0),
            default=1,
            output_field=DecimalField()
        )
        base_dc_expr = (F('nsaldo') 
                        / (dc.ndiasperiocidad if dc else 1)
        )
        if dc and dc.lsobreanticipo:
            base_dc_expr = base_dc_expr * F('documento__nporcentajeanticipo') / 100

        tasa_dcv_expr = Case(
            When(documento__cxtipofactoring__lacumulamoraatasadc=True,
                 then=F('documento__cxcliente__datos_operativos__ntasamora')
                 +F('documento__ntasadescuento')),
            default=F('documento__cxcliente__datos_operativos__ntasamora'),
            output_field=DecimalField()
        )
        dc_negociado_expr = ExpressionWrapper(
            base_dc_expr * dias_negociados_expr * F('documento__ntasadescuento') / 100
            * factor_calcular_expr,
            output_field=DecimalField()
        )
        dc_vencido_expr = ExpressionWrapper(
            base_dc_expr * dias_vencidos_expr * tasa_dcv_expr / 100,
            output_field=DecimalField()
        )

        # Anotación para gao adicional
        tasa_gaoa_expr = Case(
            When(documento__cxtipofactoring__lacumulagaoaatasagao=True,
                 then=F('documento__cxcliente__datos_operativos__ntasagaoa')
                 +F('documento__ntasacomision')),
            default=F('documento__cxcliente__datos_operativos__ntasagaoa'),
            output_field=DecimalField()
        )
        base_gaoa_expr = F('nsaldo') 

        if gaoa and gaoa.lsobreanticipo:
            base_gaoa_expr = (base_gaoa_expr 
                              * F('documento__nporcentajeanticipo') 
                              / 100)

        if gaoa and gaoa.lflat:
            dias_vencidos_ceiling = Ceil(ExpressionWrapper(
                dias_vencidos_expr / gaoa.ndiasperiocidad,
                output_field=DecimalField()
            ))
            tasa_gaoa_expr = ExpressionWrapper(
                tasa_gaoa_expr * dias_vencidos_ceiling / 100,
                output_field=DecimalField()
            )
        else:
            tasa_gaoa_expr = (tasa_gaoa_expr * dias_vencidos_expr 
                              / gaoa.ndiasperiocidad / 100)

        gao_adicional_expr = ExpressionWrapper(
            base_gaoa_expr * tasa_gaoa_expr,
            output_field=DecimalField()
        )

        # iva
        base_iva_expr = 0

        if dc.lcargaiva:
            base_iva_expr = dc_negociado_expr + dc_vencido_expr
        if gao.lcargaiva:
            base_iva_expr = base_iva_expr + gao_adicional_expr

        iva_expr = ExpressionWrapper(
            base_iva_expr * F('documento__cxasignacion__nporcentajeiva') / 100,
            output_field=DecimalField()
        )

        return qs.annotate(
            saldo = F('nsaldo'),
            saldo_anticipado = saldo_anticipado_expr,
            dias_vencidos = dias_vencidos_expr,
            dc_negociado = dc_negociado_expr,
            dc_vencido = dc_vencido_expr,
            gao_adicional = gao_adicional_expr, 
            iva = iva_expr,
            deuda = saldo_anticipado_expr + dc_negociado_expr + dc_vencido_expr + gao_adicional_expr + iva_expr
        ).order_by('documento__cxtipofactoring__cttipofactoring', 'documento__cxcliente__cxcliente__ctnombre')
    
    def provision_cargos_accesorios(self, id_empresa, fecha_corte, arr_clientes = None):
        gao = Tasas_factoring.objects\
            .filter(cxtasa="GAO", empresa=id_empresa).first()
        dc = Tasas_factoring.objects\
            .filter(cxtasa='DCAR', empresa=id_empresa).first()
        gaoa = Tasas_factoring.objects\
            .filter(cxtasa="GAOA", empresa=id_empresa).first()

        if not arr_clientes:
            qs = self.filter(leliminado=False
                           , nsaldo__gt = 0
                            , accesorio__dvencimiento__lte=fecha_corte
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
                .values("documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__cxasignacion__cxtipofactoring__cttipofactoring"
                        , "documento__ctdocumento"
                        , "documento__cxasignacion__ddesembolso"
                        , "documento__cxcliente__datos_operativos__ntasamora"
                        , "accesorio__dvencimiento"
                    ) 
            
        else:
            qs = self.filter(leliminado=False
                           , nsaldo__gt = 0
                            , documento__cxcliente__in=arr_clientes
                            , accesorio__dvencimiento__lte=fecha_corte
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
                .values("documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__cxasignacion__cxtipofactoring__cttipofactoring"
                        , "documento__ctdocumento"
                        , "documento__cxasignacion__ddesembolso"
                        , "documento__cxcliente__datos_operativos__ntasamora"
                        , "accesorio__dvencimiento"
                    ) 

        # Expresiones a usar en la anotación
        dias_negociados_expr = Cast(
            ExtractDay(
            ExpressionWrapper(
                F('accesorio__dvencimiento') - F('documento__cxasignacion__ddesembolso'),
                output_field=DateField()
            )
            ),
            IntegerField()
        )
        dias_vencidos_expr = Cast(
            ExtractDay(
            ExpressionWrapper(
                fecha_corte - F('accesorio__dvencimiento'),
                output_field=DateField()
            )
            ),
            DecimalField(max_digits=6, decimal_places=2)
        )
        saldo_anticipado_expr = ExpressionWrapper(
            F('nsaldo') * F('accesorio__nporcentajeanticipo') / 100,
            output_field=DecimalField()
        )

        # Anotación para dc negociado y vencido
        factor_calcular_expr = Case(
            When(documento__cxtipofactoring__lgeneradcenaceptacion=True, then=0),
            default=1,
            output_field=DecimalField()
        )
        base_dc_expr = (F('nsaldo') 
                        / (dc.ndiasperiocidad if dc else 1)
        )
        if dc and dc.lsobreanticipo:
            base_dc_expr = base_dc_expr * F('accesorio__nporcentajeanticipo') / 100

        tasa_dcv_expr = Case(
            When(documento__cxtipofactoring__lacumulamoraatasadc=True,
                 then=F('documento__cxcliente__datos_operativos__ntasamora')
                 +F('accesorio__ntasadescuento')),
            default=F('documento__cxcliente__datos_operativos__ntasamora'),
            output_field=DecimalField()
        )
        dc_negociado_expr = ExpressionWrapper(
            base_dc_expr * dias_negociados_expr * F('accesorio__ntasadescuento') / 100
            * factor_calcular_expr,
            output_field=DecimalField()
        )
        dc_vencido_expr = ExpressionWrapper(
            base_dc_expr * dias_vencidos_expr * tasa_dcv_expr / 100,
            output_field=DecimalField()
        )

        # Anotación para gao adicional
        tasa_gaoa_expr = Case(
            When(documento__cxtipofactoring__lacumulagaoaatasagao=True,
                 then=F('documento__cxcliente__datos_operativos__ntasagaoa')
                 +F('accesorio__ntasacomision')),
            default=F('documento__cxcliente__datos_operativos__ntasagaoa'),
            output_field=DecimalField()
        )
        base_gaoa_expr = F('nsaldo') 

        if gaoa and gaoa.lsobreanticipo:
            base_gaoa_expr = base_gaoa_expr * F('accesorio__nporcentajeanticipo') / 100

        if gaoa and gaoa.lflat:
            dias_vencidos_ceiling = Ceil(ExpressionWrapper(
                dias_vencidos_expr / gaoa.ndiasperiocidad,
                output_field=DecimalField()
            ))
            tasa_gaoa_expr = ExpressionWrapper(
                tasa_gaoa_expr * dias_vencidos_ceiling / 100,
                output_field=DecimalField()
            )
        else:
            tasa_gaoa_expr = (tasa_gaoa_expr * dias_vencidos_expr 
                              / gaoa.ndiasperiocidad / 100)

        gao_adicional_expr = ExpressionWrapper(
            base_gaoa_expr * tasa_gaoa_expr,
            output_field=DecimalField()
        )

        # iva
        base_iva_expr = 0

        if dc.lcargaiva:
            base_iva_expr = dc_negociado_expr + dc_vencido_expr
        if gao.lcargaiva:
            base_iva_expr = base_iva_expr + gao_adicional_expr

        iva_expr = ExpressionWrapper(
            base_iva_expr * F('documento__cxasignacion__nporcentajeiva') / 100,
            output_field=DecimalField()
        )

        return qs.annotate(
            saldo = F('nsaldo'),
            saldo_anticipado = saldo_anticipado_expr,
            dias_vencidos = dias_vencidos_expr,
            dc_negociado = dc_negociado_expr,
            dc_vencido = dc_vencido_expr,
            gao_adicional = gao_adicional_expr, 
            iva = iva_expr,
            deuda = saldo_anticipado_expr + dc_negociado_expr + dc_vencido_expr + gao_adicional_expr + iva_expr,
        ).order_by('documento__cxtipofactoring__cttipofactoring', 'documento__cxcliente__cxcliente__ctnombre')
    
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

    objects = Documentos_protestados_Manager()

class Recuperaciones_cabecera(ClaseModelo):
    FORMAS_DE_PAGO = (
        ('EFE', 'Efectivo'),
        ('CHE', 'Cheque'),
        ('MOV', 'Movimiento contable'),
        ('TRA', 'Transferencia'),
    )
    cxrecuperacion = models.CharField(max_length=8, )
    cxcliente = models.ForeignKey(Cliente_models.Datos_generales
        , on_delete=models.CASCADE
    )
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , on_delete=models.RESTRICT)
    cxformacobro = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dcobranza = models.DateField(auto_created=True) 
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
    lcontabilizada = models.BooleanField(default=False)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_recuperacion"
                                     , null=True)

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

        return (self.recuperacion.dcobranza - vencimiento)/timedelta(days=1)

    def vencimiento(self):
        # si es factura pura, tomo el vencimiento del documento
        # ai es accesorio, busco el cheque accesorio 
        if self.documentoprotestado.documento.cxasignacion.cxtipo=='F':
            vencimiento = self.documentoprotestado.documento.dvencimiento
        else:
            vencimiento = self.documentoprotestado.accesorio.dvencimiento

        return vencimiento

    def aplicado(self):
        if self.recuperacion.cxestado =='E' or self.recuperacion.cxestado == 'P':
            return 0
        else:
            return self.nvalorrecuperacion + self.nvalorbaja + self.nvalorbajacobranza

    def bajas(self):
        return self.nvalorbaja + self.nvalorbajacobranza

    def demoradepago(self):
        return (self.recuperacion.dcobranza - self.vencimiento())/timedelta(days=1)

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
        , on_delete=models.CASCADE
        , related_name="cliente_cobranza_cargos"
    )
    cxtipofactoring = models.ForeignKey(Tipos_factoring, null=True
        , on_delete=models.RESTRICT
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
    lcontabilizada = models.BooleanField(default=False, null=True)

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
    notadedebito = models.OneToOneField(Notas_debito_cabecera
        , related_name="debito_cuentaconjunta", on_delete=models.CASCADE)
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION
        , null=True)
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
            
    def cobranza_liquidada(self):
        if self.cxtipooperacion=='C':
            x = Documentos_cabecera.objects.filter(pk = self.operacion).first()
            return x.cxestado =='L'
        elif self.cxtipooperacion=='R':
            x = Recuperaciones_cabecera.objects.filter(pk = self.operacion).first()
            return x.cxestado =='L'
        else:
            return False

class Pagare_cabecera(ClaseModelo):
    FORMAS_DE_PAGO = (
        ('EFE', 'Efectivo'),
        ('CHE', 'Cheque'),
        ('MOV', 'Movimiento contable'),
        ('TRA', 'Transferencia'),
        ('DEP', 'Deposito de accesorio'),
    )
    cxcobranza = models.CharField(max_length=8, )
    cxcliente=models.ForeignKey(Cliente_models.Datos_generales
        , on_delete=models.CASCADE
        , related_name="cliente_cobranza_pagare"
    )
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    dcobranza = models.DateField(auto_created=True) 
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nsobrepago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cxestado = models.CharField(max_length=1, default='A')
    cxcheque = models.ForeignKey(Cheques, on_delete=models.RESTRICT
        , null=True, related_name='cheque_cobranza_pagare')
    cxcuentatransferencia = models.ForeignKey(Cliente_models.Cuentas_bancarias
        , null=True, on_delete = models.RESTRICT)
    cxcuentadeposito = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True, related_name="banco_deposito_pagare")
    # ctreferenciadeposito = models.CharField(max_length=15)
    ddeposito = models.DateTimeField(null=True) 
    cxaccesorio = models.ForeignKey(ChequesAccesorios
        , on_delete = models.RESTRICT, null=True)
    lcontabilizada = models.BooleanField(default=False, null=True)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_cobranza_pagare"
                                     , null=True)

    def __str__(self):
        return self.cxcobranza

    def movimiento(self):
        # si está protestada debe decir "cobranza protestada"
        if self.cxestado=='P' :
            x = 'Cobranza protestada'
        else:
            x = 'Cobranza'
        return x
    
class Pagare_detalle(ClaseModelo):
    cobranza =models.ForeignKey(Pagare_cabecera
        , on_delete=models.CASCADE
    )
    cuota=models.ForeignKey(Cuotas
        , on_delete=models.CASCADE
    )
    nvalorcobranza = models.DecimalField(max_digits=10, decimal_places=2)
    nvaloraplicainteres = models.DecimalField(max_digits=10, decimal_places=2
                                              , default=0)
    nsaldoaldia= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accesorioquitado = models.ForeignKey(ChequesAccesorios, on_delete=models.RESTRICT
                                        , null=True)

    def aplicado_a_capital(self):
        return self.nvalorcobranza - self.nvaloraplicainteres
    
class Factura_cuota(ClaseModelo):
    cuota=models.ForeignKey(Cuotas
        , on_delete=models.CASCADE)
    cobranzacuota=models.ForeignKey(Pagare_detalle
        , on_delete=models.CASCADE)
    nbaseiva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nbasenoiva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lfacturagenerada = models.BooleanField(default=False)
    
    def __str__(self):
        return self.cobranzacuota.cobranza.cxcobranza
    
class Protestos_historico_Manager(models.Manager):
    def TotalProtestos(self, id_empresa, id_corte):
        return self.filter(leliminado=False
                           , historico = id_corte
                           , empresa = id_empresa
                           , nsaldocartera__gt = 0)\
            .aggregate(Total = Sum('nsaldocartera'))

    def protestos_pendientes(self, id_empresa, id_corte):
        cp = self.filter(nsaldocartera__gt=0
                         , leliminado = False
                         , historico = id_corte
                         , empresa = id_empresa
                         , cxtipooperacion='C')\
            .values('id','cheque__cheque_cobranza'
                    ,'cheque__cheque_cobranza__cxcliente__cxcliente__ctnombre'
                    ,'cheque__cheque_cobranza__cxcobranza'
                    ,'cheque__cheque_cobranza__dcobranza'
                    ,'cheque__cheque_cobranza__ddeposito'
                    ,'cheque__ctgirador','dprotesto'
                    ,'motivoprotesto__ctmotivoprotesto'
                    ,'nvalor','nsaldocartera','nvalorcartera', 'cheque__cxparticipante'
                    )
        rp = self.filter(nsaldocartera__gt=0
                         , leliminado = False
                         , historico = id_corte
                         , empresa = id_empresa
                         , cxtipooperacion='R')\
            .values('id','cheque__cheque_recuperacion'
                    ,'cheque__cheque_recuperacion__cxcliente__cxcliente__ctnombre'
                    ,'cheque__cheque_recuperacion__cxrecuperacion'
                    ,'cheque__cheque_recuperacion__dcobranza'
                    ,'cheque__cheque_recuperacion__ddeposito'
                    ,'cheque__ctgirador','dprotesto'
                    ,'motivoprotesto__ctmotivoprotesto'
                    ,'nvalor','nsaldocartera','nvalorcartera', 'cheque__cxparticipante'
                    )
        return cp.union(rp)
        
    # def protestos_pendientes_cliente(self, id_empresa, id_cliente):
    #     cp = self.filter(nsaldocartera__gt=0
    #                      , leliminado = False
    #                      , empresa = id_empresa
    #                      , cheque__cheque_cobranza__cxcliente = id_cliente
    #                      , cxtipooperacion='C')\
    #         .values('id','cheque__cheque_cobranza'
    #                 ,'cheque__cheque_cobranza__cxcliente__cxcliente__ctnombre'
    #                 ,'cheque__cheque_cobranza__cxcobranza'
    #                 ,'cheque__cheque_cobranza__dcobranza'
    #                 ,'cheque__cheque_cobranza__ddeposito'
    #                 ,'cheque__ctgirador','dprotesto'
    #                 ,'motivoprotesto__ctmotivoprotesto'
    #                 ,'nvalor','nsaldocartera','nvalorcartera'
    #                 )
    #     rp = self.filter(nsaldocartera__gt=0
    #                      , leliminado = False
    #                      , empresa = id_empresa
    #                      , cheque__cheque_recuperacion__cxcliente = id_cliente
    #                      , cxtipooperacion='R')\
    #         .values('id','cheque__cheque_recuperacion'
    #                 ,'cheque__cheque_recuperacion__cxcliente__cxcliente__ctnombre'
    #                 ,'cheque__cheque_recuperacion__cxrecuperacion'
    #                 ,'cheque__cheque_recuperacion__dcobranza'
    #                 ,'cheque__cheque_recuperacion__ddeposito'
    #                 ,'cheque__ctgirador','dprotesto'
    #                 ,'motivoprotesto__ctmotivoprotesto'
    #                 ,'nvalor','nsaldocartera','nvalorcartera'
    #                 )
    #     return cp.union(rp)
        
    # def TotalProtestosCliente(self, id_cliente):
    #     return self.filter(leliminado=False
    #                        , nsaldocartera__gt = 0)\
    #                 .filter(Q(cheque__cheque_cobranza__cxcliente = id_cliente
    #                           , cxtipooperacion='C')
    #                         |Q(cheque__cheque_recuperacion__cxcliente = id_cliente
    #                            , cxtipooperacion='R'))\
    #         .aggregate(Total = Sum('nsaldocartera'))

class Cheques_protestados_historico(ClaseModelo):
    FORMAS_DE_COBRO = (
        ('CHE', 'Cheque'),
        ('DEP', 'Deposito de accesorio'),
    )
    TIPO_OPERACION = (
        ("C", "Cobranza"),
        ("R","Recuperacion"),
    )
    cheque = models.ForeignKey(Cheques, on_delete= models.RESTRICT
        , related_name="cheque_protestado_historico")
    cxformacobro = models.CharField(max_length=3, choices=FORMAS_DE_COBRO)
    dprotesto = models.DateField()
    motivoprotesto = models.ForeignKey(Motivos_protesto_maestro
        , on_delete=models.RESTRICT)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    nvalorcartera = models.DecimalField(max_digits=10, 
                                        decimal_places=2, default=0)
    nsaldocartera =  models.DecimalField(max_digits=10, 
                                         decimal_places=2)
    cxestado = models.CharField(max_length=1, default="A") 
    dultimacobranza = models.DateTimeField(null=True) 
    cxtipooperacion = models.CharField(max_length=1, 
                                       choices=TIPO_OPERACION)
    notadedebito = models.ForeignKey(Notas_debito_cabecera, 
                                     on_delete=models.CASCADE, 
                                     null=True)
    lcontabilizada = models.BooleanField(default=False)
    asiento = models.OneToOneField(Diario_cabecera, 
                                   on_delete=models.RESTRICT
                                    , related_name="asiento_protesto_historico"
                                    , null=True)
    historico= models.ForeignKey(Cortes_historico, 
                                 on_delete=models.RESTRICT
        , related_name="cheque_protestado_historico")
    idanterior = models.BigIntegerField(default=0)

    objects = Protestos_historico_Manager()

    def __str__(self):
        return '{} CH/{}'.format(self.cheque.cxcuentabancaria, self.cheque.ctcheque)        

class Documentos_protestados_historico_Manager(models.Manager):

    def antigüedad_cartera(self, id_empresa, id_corte):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        protestados = self.filter( leliminado = False
                                  , nsaldo__gt = 0
                                  , historico = id_corte
                                , empresa = id_empresa)\
            .aggregate(
                fvencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90
                                , accesorio__isnull = True) ) 
                , avencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo90
                                , accesorio__isnull = False) ) 
                , fvencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90
                                , accesorio__isnull = True) ) 
                , avencido_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo60
                                , accesorio__dvencimiento__gte = vcdo90
                                , accesorio__isnull = False) ) 
                , fvencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                , documento__dvencimiento__gte = vcdo60
                                , accesorio__isnull = True) ) 
                , avencido_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo30
                                , accesorio__dvencimiento__gte = vcdo60
                                , accesorio__isnull = False) ) 
                , fvencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                , documento__dvencimiento__gte = vcdo30
                                , accesorio__isnull = True) ) 
                , avencido_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = datetime.today()
                                , accesorio__dvencimiento__gte = vcdo30
                                , accesorio__isnull = False) ) 
                ,fporvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                , documento__dvencimiento__lte = xver30
                                , accesorio__isnull = True) ) 
                ,aporvencer_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gte = datetime.today()
                                , accesorio__dvencimiento__lte = xver30
                                , accesorio__isnull = False ) )
                ,fporvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                , documento__dvencimiento__lte = xver60
                                , accesorio__isnull = True) ) 
                ,aporvencer_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver30
                                , accesorio__dvencimiento__lte = xver60
                                , accesorio__isnull = False) ) 
                ,fporvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                , documento__dvencimiento__lte = xver90
                                , accesorio__isnull = True) ) 
                ,aporvencer_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver60
                                , accesorio__dvencimiento__lte = xver90
                                , accesorio__isnull = False) ) 
                , fporvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90
                                , accesorio__isnull = True)) 
                , aporvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver90
                                , accesorio__isnull = False)) 
                )
        fvm90 = protestados["fvencido_mas_90"] or 0
        fv90 = protestados["fvencido_90"] or 0
        fv60 = protestados["fvencido_60"] or 0
        fv30 = protestados["fvencido_30"] or 0
        fx30 = protestados["fporvencer_30"] or 0
        fx60 = protestados["fporvencer_60"] or 0
        fx90 = protestados["fporvencer_90"] or 0
        fxm90 = protestados["fporvencer_mas_90"] or 0
        avm90=protestados["avencido_mas_90"] or 0
        av90=protestados["avencido_90"] or 0
        av60=protestados["avencido_60"] or 0
        av30=protestados["avencido_30"] or 0
        ax30=protestados["aporvencer_30"] or 0
        ax60=protestados["aporvencer_60"] or 0
        ax90=protestados["aporvencer_90"] or 0
        axm90=protestados["aporvencer_mas_90"] or 0

        protestos={}

        protestos["pvencido_mas_90"] = fvm90+avm90
        protestos["pvencido_90"] = fv90+av90
        protestos["pvencido_60"] = fv60+av60
        protestos["pvencido_30"] = fv30+av30
        protestos["pporvencer_30"] = fx30+ax30
        protestos["pporvencer_60"] = fx60+ax60
        protestos["pporvencer_90"] = fx90+ax90
        protestos["pporvencer_mas_90"] = fxm90+axm90

        return protestos
    
    def antigüedad_por_cliente_facturas(self, id_empresa, id_corte):
        # la fecha de vencimiento está en el documento
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                            , historico = id_corte
                           , nsaldo__gt = 0
                           , accesorio__isnull = True
                           , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90) ) 
                , vencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                , documento__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                , documento__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                , documento__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                , documento__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                , documento__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90))
                , total = Sum('nsaldo')
                )\
            .order_by()
    
    def antigüedad_por_cliente_accesorios(self, id_empresa, id_corte):
        # la fecha de vencimiento está en el accesorio
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                            , historico = id_corte
                           , nsaldo__gt = 0
                           , accesorio__isnull = False
                           , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo60
                                , accesorio__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = vcdo30
                                , accesorio__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__lt = datetime.today()
                                , accesorio__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gte = datetime.today()
                                , accesorio__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver30
                                , accesorio__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver60
                                , accesorio__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__dvencimiento__gt = xver90))
                , total = Sum('nsaldo')
                )\
            .order_by()
    
    # def revision_cartera(self, id_empresa):
    #     # si tiene accesorio, la fecha de vencimiento es la del accesorio
    #     # si no tiene accesorio, la fecha de vencimiento es la del documento
    #     vcdo30 = datetime.today() + timedelta(days=-30)
    #     # xver30 = datetime.today() + timedelta(days=30)

    #     return self.filter(leliminado=False, nsaldo__gt=0, empresa=id_empresa) \
    #         .values('documento__cxcliente__cxcliente__ctnombre',
    #                 'documento__cxcliente__linea_factoring__nvalor',
    #                 'documento__cxcliente__datos_operativos__cxclase__cxclase',
    #                 'documento__cxcliente__datos_operativos__cxestado',
    #                 'documento__cxcliente',
    #                 ) \
    #         .annotate(
    #             vencido_mas_30=Value(0, output_field=DecimalField()),
    #             vencido_30=Value(0, output_field=DecimalField()),
    #             por_vencer=Value(0, output_field=DecimalField()),
    #             ptotesto=Sum('nsaldo'),
    #             total=Sum('nsaldo')
    #         ) \
    #         .order_by()
    
class Documentos_protestados_historico(ClaseModelo):
    chequeprotestado = models.ForeignKey(Cheques_protestados_historico
                                         , on_delete= models.RESTRICT)
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
    historico= models.ForeignKey(Cortes_historico, on_delete=models.RESTRICT
        , related_name="documento_protestado_historico")

    objects = Documentos_protestados_historico_Manager()

class Gestion_cobro(ClaseModelo):
    TIPOS_DE_PARTICIPANTE = (
        ('C', 'Cliente'),
        ('D', 'Deudor'),
    )
    ESTADOS_DE_GESTION = (
        ('A', 'Abierta'),
        ('C', 'Cerrada'),
        ('P', 'Pendiente'),
        ('R', 'Reprogramada'),
    )
    cxtipoparticipante = models.CharField(max_length=1, choices=TIPOS_DE_PARTICIPANTE)
    revision_cartera_cliente = models.ForeignKey(Revision_cartera_detalle
        , on_delete=models.CASCADE, null=True, related_name="revision_cartera_cliente")
    cxestado = models.CharField(max_length=1, default='P', choices=ESTADOS_DE_GESTION)
    ctnumerowhatsapp = models.CharField(max_length=20, null=True, blank=True
        , verbose_name='Número de WhatsApp')

    def __str__(self):
        if self.cxtipoparticipante == 'C':
            return f'Cliente: {self.revision_cartera_cliente.cxcliente.cxcliente.ctnombre}'
        # else:
        #     return f'Deudor: {self.revision_cartera_cliente.documento.ctdeudor}'
    def estado(self):
        return self.get_cxestado_display()

class Twilio_whatsapp(ClaseModelo):
    configuracion = models.ForeignKey(Configuracion_twilio_whatsapp, on_delete=models.CASCADE)
    gestion_cobro = models.ForeignKey(Gestion_cobro, on_delete=models.CASCADE
        , related_name="gestion_cobro_whatsapp", )
    ctfrom = models.CharField(max_length=25, verbose_name='De')
    ctto = models.CharField(max_length=25, verbose_name='Para')
    ctbody = models.TextField(verbose_name='Mensaje')
    ctsid = models.CharField(max_length=100, unique=True, verbose_name='SID')
    ctstatus = models.CharField(max_length=20, verbose_name='Estado')
    ctdirection = models.CharField(max_length=30, verbose_name='Dirección')
    jcontexto = models.JSONField(verbose_name='Contexto', )

    def __str__(self):
        return self.ctsid

    class Meta:
        verbose_name = 'Mensaje de WhatsApp'
        verbose_name_plural = 'Mensajes de WhatsApp'