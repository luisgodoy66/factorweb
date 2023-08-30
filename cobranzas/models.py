# from email.policy import default
# from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Q

from datetime import timedelta, datetime, date

from bases.models import ClaseModelo
from empresa.models import Datos_participantes , Tipos_factoring, Cuentas_bancarias
from clientes import models as Cliente_models
from operaciones.models import Documentos, ChequesAccesorios\
    , Cargos_detalle as Operaciones_cargos, Motivos_protesto_maestro
from cuentasconjuntas import models as CuentasConjuntasModels

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
    accesorioquitado = models.ForeignKey(ChequesAccesorios, on_delete=models.RESTRICT
                                        , null=True)

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
    niva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
                    ,'nvalor','nsaldocartera','nvalorcartera'
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
                    ,'nvalor','nsaldocartera','nvalorcartera'
                    )
        return cp.union(rp)
        
    def TotalProtestosCliente(self, id_cliente):
        print(id_cliente)
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
    lcontabilizada = models.BooleanField(default=False, null=True)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_protesto"
                                     , null=True)

    objects = Protestos_Manager()

    def __str__(self):
        return '{} CH/{}'.format(self.cheque.cxcuentabancaria, self.cheque.ctcheque)        

class Documentos_protestados_Manager(models.Manager):

    def antigüedad_cartera(self, id_empresa):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        protestados = self.filter( leliminado = False, nsaldo__gt = 0
                                , empresa = id_empresa)\
            .aggregate(
                fvencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90
                                , accesorio__isnull = True) ) 
                , avencido_mas_90 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__lt = vcdo90
                                , accesorio__isnull = False) ) 
                , fvencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90
                                , accesorio__isnull = True) ) 
                , avencido_90 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90
                                , accesorio__isnull = False) ) 
                , fvencido_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo30
                                , documento__dvencimiento__gte = vcdo60
                                , accesorio__isnull = True) ) 
                , avencido_60 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__lt = vcdo30
                                , documento__dvencimiento__gte = vcdo60
                                , accesorio__isnull = False) ) 
                , fvencido_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = datetime.today()
                                , documento__dvencimiento__gte = vcdo30
                                , accesorio__isnull = True) ) 
                , avencido_30 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__lt = datetime.today()
                                , documento__dvencimiento__gte = vcdo30
                                , accesorio__isnull = False) ) 
                ,fporvencer_30 = Sum('nsaldo', filter=Q(documento__dvencimiento__gte = datetime.today()
                                , documento__dvencimiento__lte = xver30
                                , accesorio__isnull = True) ) 
                ,aporvencer_30 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__gte = datetime.today()
                                , documento__dvencimiento__lte = xver30
                                , accesorio__isnull = False ) )
                ,fporvencer_60 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver30
                                , documento__dvencimiento__lte = xver60
                                , accesorio__isnull = True) ) 
                ,aporvencer_60 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__gt = xver30
                                , documento__dvencimiento__lte = xver60
                                , accesorio__isnull = False) ) 
                ,fporvencer_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver60
                                , documento__dvencimiento__lte = xver90
                                , accesorio__isnull = True) ) 
                ,aporvencer_90 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__gt = xver60
                                , documento__dvencimiento__lte = xver90
                                , accesorio__isnull = False) ) 
                , fporvencer_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__gt = xver90
                                , accesorio__isnull = True)) 
                , aporvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio__documento__dvencimiento__gt = xver90
                                , accesorio__isnull = False)) 
                )
        fvm90 = protestados["fvencido_mas_90"]
        avm90=protestados["avencido_mas_90"]
        fv90 = protestados["fvencido_90"]
        av90=protestados["avencido_90"]
        fv60 = protestados["fvencido_60"]
        av60=protestados["avencido_60"]
        fv30 = protestados["fvencido_30"]
        av30=protestados["avencido_30"]
        fx30 = protestados["fporvencer_30"]
        ax30=protestados["aporvencer_30"]
        fx60 = protestados["fporvencer_60"]
        ax60=protestados["aporvencer_60"]
        fx90 = protestados["fporvencer_90"]
        ax90=protestados["aporvencer_90"]
        fxm90 = protestados["fporvencer_mas_90"]
        axm90=protestados["aporvencer_mas_90"]
        if not fvm90: fvm90=0
        if not fv90: fv90=0
        if not fv60: fv60=0
        if not fv30: fv30=0
        if not fx30: fx30=0
        if not fx60: fx60=0
        if not fx90: fx90=0
        if not fxm90: fxm90=0
        if not avm90: avm90=0
        if not av90: av90 = 0
        if not av60: av60 = 0
        if not av30: av30 = 0
        if not ax30: ax30 = 0
        if not ax60: ax60 = 0
        if not ax90: ax90 = 0
        if not axm90: axm90 = 0

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
                vencido_mas_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(documento__dvencimiento__lt = vcdo60
                                , documento__dvencimiento__gte = vcdo90))
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
    lcontabilizada = models.BooleanField(default=False, null=True)

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
