from random import choices
from django.db import models
from django.forms import BooleanField
from django.db.models import Sum, Q

from bases.models import ClaseModelo
from empresa.models import Clases_cliente, Datos_participantes \
    , Tipos_documentos, Tipos_factoring, Cuentas_bancarias
from clientes.models import Datos_generales as Datos_generales_cliente\
    , Cuenta_transferencia
from pais.models import Bancos

from datetime import datetime, timedelta, date

class Datos_operativos(ClaseModelo):
    ESTADOS_DE_CLIENTES = (
        ('A', 'Activo'),
        ('B', 'Baja'),
        ('I', 'Inactivo'),
        ('P', 'Pre legal'),
        ('L', 'Legal'),
        ('X', 'Bloqueado'),
    )
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
        , related_name="datos_operativos"
    )
    dalta = models.DateTimeField(auto_created=True) 
    cxtipoliquidacioncobranza = models.CharField(max_length=1, default="L", null=True) 
    cxclase =models.ForeignKey(Clases_cliente
        ,to_field="cxclase", default='A', on_delete=models.DO_NOTHING
    )
    nporcentajeanticipo = models.SmallIntegerField(default= 80)
    ntasacomision = models.DecimalField(max_digits=11, decimal_places=8, default=0) 
    ntasadescuentocartera = models.DecimalField(max_digits=11, decimal_places=8, default = 0)
    ntasagaoa= models.DecimalField(max_digits=11, decimal_places=8, default=0) 
    cxbeneficiarioasignacion = models.CharField(max_length=13, blank=True, null=True)
    ctbeneficiarioasignacion = models.TextField(blank=True, null=True)
    cxbeneficiariocobranzas = models.CharField(max_length=13, blank=True, null=True)
    ctbeneficiariocobranzas = models.TextField(blank=True, null=True)
    cxestado=models.CharField(max_length=1, default='A', choices=ESTADOS_DE_CLIENTES  )
    dultimanegociacion = models.DateField(null=True)

    def __str__(self):
        return self.cxcliente.cxcliente.ctnombre
  
class Asignacion(ClaseModelo):
    TIPOS_DE_ASIGNACION = (
        ('A', 'Con accesorios'),
        ('F', 'Facturas puras'),
    )
    ESTADOS_DE_ASIGNACION = (
        ('L', 'Liquidada'),
        ('P', 'Pagada'),
    )
    cxcliente=models.ForeignKey(Datos_participantes
        ,to_field="cxparticipante", on_delete=models.CASCADE
        , related_name="cliente_asignacion"
    )
    cxasignacion = models.CharField(max_length=8 ) 
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , to_field="cxtipofactoring", on_delete=models.RESTRICT
        , related_name="tipofactoring_asignacion")
    cxtipo = models.CharField(max_length=1, choices=TIPOS_DE_ASIGNACION) 
    cxmodalidadfactoring = models.CharField(max_length=1) 
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dnegociacion = models.DateTimeField(auto_created=True) 
    ddesembolso= models.DateField(auto_created=True) 
    nvalor = models.DecimalField(max_digits=15, decimal_places =2) 
    nanticipo = models.DecimalField(max_digits=10, decimal_places= 2, default=0)
    # cxexcesolineafactoring = models.CharField(max_length=6) 
    cxestado = models.CharField(max_length=1, default="L", 
        choices=ESTADOS_DE_ASIGNACION) 
    ctbancochequegarantia = models.CharField(max_length=25, blank=True, null=True) 
    ctcuentachequegarantia = models.CharField(max_length=15, blank=True, null=True) 
    ctnumerochequegarantia = models.CharField(max_length=7, blank=True, null=True) 
    dchequegaratia = models.DateTimeField(auto_created=True, null=True) 
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    ndescuentodecartera = models.DecimalField(max_digits=10,
        decimal_places= 2, default= 0)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    ctinstrucciondepago = models.TextField(blank=True)
    nretencionenfactura = models.DecimalField(max_digits=10 ,
        decimal_places= 2, default= 0)
    lcartacesiongenerada = models.BooleanField(default=False, null=True) 
    nmayorplazonegociacion = models.SmallIntegerField(default=0, )

    def __str__(self):
        return self.cxasignacion

    def neto(self):
        return self.nanticipo - self.ngao - self.ndescuentodecartera - self.niva

class Documentos_Manager(models.Manager):
    def facturas_pendientes(self,fecha_corte):
        return self.filter(dvencimiento__lte = fecha_corte
                , leliminado = False, nsaldo__gt = 0
                , cxasignacion__in = Asignacion.objects
                    .filter(cxtipo = "F", cxestado = "P", leliminado = False))
                # Cambiar a tipo F-actura y estado P-agada
                # .filter(cxtipo = "P", cxestado = "L"))\

    def antigüedad_cartera(self):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , cxasignacion__cxtipo = "F"
            , cxasignacion__cxestado = "P"
            , cxasignacion__leliminado = False)\
            .aggregate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(dvencimiento__lt = vcdo60
                    , dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(dvencimiento__lt = vcdo30
                    , dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(dvencimiento__lt = datetime.today()
                    , dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(dvencimiento__gte = datetime.today()
                    , dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(dvencimiento__gt = xver30
                    , dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(dvencimiento__gt = xver60
                    , dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(dvencimiento__gt = xver90) ) 
                )
    
    def antigüedad_por_cliente(self):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , cxasignacion__cxtipo = "F"
            , cxasignacion__cxestado = "P"
            , cxasignacion__leliminado = False)\
            .values('cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(dvencimiento__lt = vcdo60
                    , dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(dvencimiento__lt = vcdo30
                    , dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(dvencimiento__lt = datetime.today()
                    , dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(dvencimiento__gte = datetime.today()
                    , dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(dvencimiento__gt = xver30
                    , dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(dvencimiento__gt = xver60
                    , dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(dvencimiento__gt = xver90) ) 
                , total = Sum('nsaldo')
                )\
            .order_by()

    def TotalCartera(self):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , cxasignacion__cxestado = "P"
                           , cxasignacion__leliminado = False)\
            .aggregate(Total = Sum('nsaldo'))

class Documentos(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_participantes
        ,to_field="cxparticipante", on_delete=models.CASCADE
        , related_name="cliente_documento"
    )
    cxasignacion=models.ForeignKey(Asignacion
        , on_delete=models.CASCADE
    )
    cxtipofactoring=models.ForeignKey(Tipos_factoring
        ,to_field="cxtipofactoring", on_delete=models.CASCADE
        , related_name="tipo_factoring"
    )
    nreferencia = models.BigIntegerField(null=True)  
    cxcomprador=models.ForeignKey(Datos_participantes
        ,to_field="cxparticipante", on_delete=models.CASCADE
        , related_name="comprador"
    )
    cxtipodocumento=models.ForeignKey(Tipos_documentos
        ,to_field="cxtipodocumento", on_delete=models.CASCADE
        , related_name="tipo_documento"
    )
    ctdocumento = models.CharField(max_length=20) 
    demision  = models.DateField() 
    dvencimiento  = models.DateField() 
    ntotal = models.DecimalField(max_digits= 15,decimal_places= 2) 
    nsaldo = models.DecimalField(max_digits= 15,decimal_places= 2) 
    cxestado = models.CharField(max_length=1, default="A") 
    nporcentajeanticipo = models.DecimalField(max_digits=5,decimal_places= 2)
    ntasadescuento = models.DecimalField(max_digits=11,decimal_places= 8)
    ntasacomision = models.DecimalField(max_digits=11,decimal_places= 8)
    nvalorantesiva = models.DecimalField(max_digits=15,decimal_places= 2)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    nretencioniva = models.DecimalField(max_digits=10,decimal_places= 2
                                        , default=0)
    nretencionrenta = models.DecimalField(max_digits=10,decimal_places= 2
                                          , default=0) 
    nvalornonegociado = models.DecimalField(max_digits=10,decimal_places= 2
                                            , default=0) 
    dultimacobranza = models.DateTimeField(null=True) 
    ndiasprorroga= models.SmallIntegerField(default=0, null=True)
    lnotificaciongenerada=models.BooleanField(default=False)
    # cxmodalidadcobranza = models.CharField(max_length=3) ,
    # npreciocompra = models.DecimalField(max_digits=10,6),
    cxpignorado = models.CharField(max_length=3, null=True) 
    cxusuarioprorroga = models.CharField(max_length=10, null=True) 
    dultimageneraciondecargos= models.DateField(null=True) 
    lcastigada=models.BooleanField(default=False, null=True)
    nanticipo = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ndescuentocartera = models.DecimalField(max_digits=10,decimal_places= 2
                                            , default=0)
    nplazo = models.IntegerField(default=0)
    nplazoap = models.IntegerField(default=0, null=True)
    ntasacomisionap = models.DecimalField(max_digits=11,decimal_places= 8
                                          , default=0, null=True)
    ntasadescuentoap = models.DecimalField(max_digits=11,decimal_places= 8
                                           , default=0, null=True)
    ngaoaap = models.DecimalField(max_digits=10,decimal_places= 2, default=0
                                  , null=True)
    ndescuentocarteraap = models.DecimalField(max_digits=10,decimal_places= 2
                                              , default=0, null=True)
                                            
    objects= Documentos_Manager()

    def __str__(self):
        return self.ctdocumento

    def dias_vencidos(self):
        return (date.today() - self.dvencimiento)/timedelta(days=1)

class ChequesAccesorios_Manager(models.Manager):

    def cheques_a_depositar(self, fecha_corte):
        return self.filter(dvencimiento__lte = fecha_corte, cxestado = 'A'
                , leliminado = False, lcanjeado = False, laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False)
            # cambiar a estado P-agada
            # .filter(documento__cxasignacion__in =Asignacion.objects.filter(cxestado = "L"))

    def facturas_pendientes(self, fecha_corte):
        return self.filter(dvencimiento__lte = fecha_corte
                , laccesorioquitado = True, chequequitado__cxestado = 'A'
                , leliminado = False, lcanjeado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False)

    def antigüedad_cartera(self):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False, lcanjeado  = False, laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False)\
            .aggregate(
                vencido_mas_90 = Sum('ntotal', filter=Q(dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('ntotal', filter=Q(dvencimiento__lt = vcdo60
                    , dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('ntotal', filter=Q(dvencimiento__lt = vcdo30
                    , dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('ntotal', filter=Q(dvencimiento__lt = datetime.today()
                    , dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('ntotal', filter=Q(dvencimiento__gte = datetime.today()
                    , dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('ntotal', filter=Q(dvencimiento__gt = xver30
                    , dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('ntotal', filter=Q(dvencimiento__gt = xver60
                    , dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('ntotal', filter=Q(dvencimiento__gt = xver90) ) 
                )

    def antigüedad_por_cliente(self):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False, lcanjeado  = False, laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False)\
            .values('documento__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('ntotal', filter=Q(dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('ntotal', filter=Q(dvencimiento__lt = vcdo60
                    , dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('ntotal', filter=Q(dvencimiento__lt = vcdo30
                    , dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('ntotal', filter=Q(dvencimiento__lt = datetime.today()
                    , dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('ntotal', filter=Q(dvencimiento__gte = datetime.today()
                    , dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('ntotal', filter=Q(dvencimiento__gt = xver30
                    , dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('ntotal', filter=Q(dvencimiento__gt = xver60
                    , dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('ntotal', filter=Q(dvencimiento__gt = xver90) ) 
                , total = Sum('ntotal')
                )\
            .order_by()

class Cheques_quitados_Manager(models.Manager):
    def antigüedad_cartera(self):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False
                , accesorio_quitado__documento__cxasignacion__cxestado = "P"
                , accesorio_quitado__documento__cxasignacion__leliminado = False)\
            .aggregate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = vcdo60
                    , accesorio_quitado__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = vcdo30
                    , accesorio_quitado__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = datetime.today()
                    , accesorio_quitado__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gte = datetime.today()
                    , accesorio_quitado__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gt = xver30
                    , accesorio_quitado__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gt = xver60
                    , accesorio_quitado__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gt = xver90) ) 
                )

    def antigüedad_por_cliente(self):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False
                , accesorio_quitado__documento__cxasignacion__cxestado = "P"
                , accesorio_quitado__documento__cxasignacion__leliminado = False)\
            .values('accesorio_quitado__documento__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = vcdo60
                    , accesorio_quitado__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = vcdo30
                    , accesorio_quitado__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = datetime.today()
                    , accesorio_quitado__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gte = datetime.today()
                    , accesorio_quitado__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gt = xver30
                    , accesorio_quitado__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gt = xver60
                    , accesorio_quitado__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gt = xver90) ) 
                , total = Sum('nsaldo')
                )

class Cheques_quitados(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
    )
    cxestado = models.CharField(max_length=1, default="A") 
    nsaldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ctmotivoquitado = models.CharField(max_length=60)
    dultimacobranza = models.DateTimeField(null=True) 
            
    objects = Cheques_quitados_Manager()

class ChequesAccesorios(ClaseModelo):
    PROPIETARIO = (
        ('C', 'Cliente'),
        ('D', 'Deudor'),
    )
    cxpropietariocuenta = models.CharField(max_length=1, choices= PROPIETARIO
        , default='D')
    documento = models.ForeignKey(Documentos
        , on_delete=models.CASCADE, related_name="documento_cheque")
    cxbanco = models.ForeignKey(Bancos, on_delete=models.RESTRICT
        , related_name="banco_cheque_operacion")
    ctcuenta = models.CharField(max_length=15)
    ctcheque = models.CharField(max_length=8) 
    ctplaza = models.CharField(max_length=30, null=True)  
    ctgirador = models.CharField(max_length=60) 
    ntotal = models.DecimalField(max_digits= 10,decimal_places= 2) 
    dvencimiento  = models.DateField() 
    nporcentajeanticipo = models.DecimalField(max_digits=5,decimal_places= 2)
    ntasacomision = models.DecimalField(max_digits=11,decimal_places= 8)
    ntasadescuento = models.DecimalField(max_digits=11,decimal_places= 8)
    nanticipo = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default=0)
    ndescuentocartera = models.DecimalField(max_digits=10,decimal_places= 2
                                            , default=0)
    nplazo = models.IntegerField(default=0)
    cxestado = models.CharField(max_length=1, default="A") 
    ddeposito = models.DateTimeField( null= True) 
    lcanjeado = models.BooleanField(default=False)
    ncanjeadopor = models.BigIntegerField(null=True)
    laccesorioquitado = models.BooleanField(default= False, null=True)
    chequequitado = models.ForeignKey(Cheques_quitados, on_delete=models.RESTRICT
        , related_name="accesorio_quitado", null=True)
    dultimageneraciondecargos= models.DateField(null=True) 
    nplazoap = models.IntegerField(default=0, null=True)
    ntasacomisionap = models.DecimalField(max_digits=11,decimal_places= 8
                                          , default=0, null=True)
    ntasadescuentoap = models.DecimalField(max_digits=11,decimal_places= 8
                                           , default=0, null=True)
    ngaoaap = models.DecimalField(max_digits=10,decimal_places= 2, default=0
                                  , null=True)
    ndescuentocarteraap = models.DecimalField(max_digits=10,decimal_places= 2
                                              , default=0, null=True)
    
    objects= ChequesAccesorios_Manager()

    def __str__(self):
        return '{} CTA.{} CH/{}'.format(self.cxbanco,self.ctcuenta, self.ctcheque)

    def dias_vencidos(self):
        return (date.today() - self.dvencimiento)/timedelta(days=1)

class Movimientos_maestro(ClaseModelo):
    TIPOS_DE_SIGNOS = (
        ('+', 'Suma'),
        ('-', 'Resta'),
    )
    cxmovimiento = models.CharField(max_length=4, unique=True) 
    ctmovimiento= models.CharField(max_length=60) 
    cxsigno= models.CharField(max_length=1, choices=TIPOS_DE_SIGNOS) 
    # lcargadescuentocartera = models.BooleanField()
    nprioridad = models.SmallIntegerField()
    lcolateral = models.BooleanField()
    cxmovimientopadre = models.CharField(max_length=4) 

    def __str__(self):
        return self.ctmovimiento

    def save(self):
        self.cxmovimiento=self.cxmovimiento.upper()
        return super(Movimientos_maestro, self).save()

class Movimientos_clientes(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
        , related_name="movimientos"
    )
    cxtipofactoring = models.CharField(max_length=3, null=True) 
    cxmovimiento = models.ForeignKey(Movimientos_maestro
        , to_field="cxmovimiento", on_delete=models.CASCADE
        , related_name="maestro_movimientos") 
    nvalor = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    cxoperacion = models.CharField(max_length=10) 
    dmovimiento = models.DateField() 
    
    def __str__(self):
        return self.cxcliente

class Cargos_detalle(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
        , related_name="cargos"
    )
    cxtipofactoring = models.CharField(max_length=3, null=True) 
    cxasignacion = models.ForeignKey(Asignacion, on_delete=models.RESTRICT
        , null=True) 
    cxdocumento  = models.ForeignKey(Documentos, on_delete=models.RESTRICT
        , null=True)  
    cxmovimiento = models.ForeignKey(Movimientos_maestro
        ,to_field="cxmovimiento", on_delete=models.RESTRICT)
    nvalor = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    nsaldo = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    dultimageneracioncargos = models.DateField()
    ctvalorbase  = models.CharField(max_length=15 ) 
    ndiascalculo = models.SmallIntegerField()
    ntasacalculo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lgeneraprocesocontable = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.cxmovimiento.ctmovimiento
        
class Condiciones_operativas_cabecera(ClaseModelo):
    ctcondicion = models.CharField(max_length=40)
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        ,to_field="cxtipofactoring", on_delete=models.CASCADE)
    lactiva = models.BooleanField(default=True)
    laplicaafacturaspuras = models.BooleanField(default=True)
    laplicaaaccesorios = models.BooleanField(default=True)

    def __str__(self):
        return self.ctcondicion

class Condiciones_Operativas_Manager(models.Manager):
    def ubicar_plazo(self, condicion, clase_cliente, clase_comprador, plazo=0):
        return self.filter(leliminado = False)\
            .filter(cxcondicion = condicion)\
            .filter(cxclasecliente = clase_cliente)\
            .filter(cxclasecomprador=clase_comprador)\
            .filter(nplazodesde__lte = plazo)\
            .filter(nplazohasta__gte = plazo)
            
class Condiciones_operativas_detalle(ClaseModelo):
    cxcondicion = models.ForeignKey(Condiciones_operativas_cabecera
        , on_delete=models.CASCADE)
    cxclasecliente = models.ForeignKey(Clases_cliente
        , related_name="clase_cliente", on_delete=models.CASCADE)
    cxclasecomprador = models.ForeignKey(Clases_cliente
        , related_name="clases_compradores", on_delete=models.CASCADE)
    nplazodesde = models.SmallIntegerField()
    nplazohasta = models.SmallIntegerField()
    nporcentajeanticipo = models.SmallIntegerField()
    ntasadescuento = models.DecimalField(max_digits=5, decimal_places=2)
    ntasagao = models.DecimalField(max_digits=5, decimal_places=2)

    objects = Condiciones_Operativas_Manager()

    def __str__(self):
        return self.cxcondicion

class Anexos(ClaseModelo):
    ctnombre = models.TextField(unique=True)
    lactivo = models.BooleanField(default=True)
    ctrutageneracion = models.TextField()
    ctrutaanexo = models.TextField()
    def __str__(self):
        return self.ctnombre
        
class Desembolsos(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('A', 'Asignaciones'),
        ('C', 'Cobranzas'),
    )
    FORMAS_DE_PAGO = (
        ('EFE', 'Efectivo'),
        ('CHE', 'Cheque'),
        ('MOV', 'Movimiento contable'),
        ('TRA', 'Transferencia'),
    )
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION)
    cxoperacion = models.BigIntegerField()
    cxcliente = models.ForeignKey(Datos_generales_cliente, on_delete=models.RESTRICT
        , null = True)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxcuentapago = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True)
    cxbeneficiario = models.CharField(max_length=13, blank=True, null=True)
    ctbeneficiario = models.TextField(blank=True, null=True)
    cxcuentadestino = models.ForeignKey(Cuenta_transferencia
        , on_delete=models.RESTRICT, null = True)
    lgeneradoarchivobanco = models.BooleanField(default=False)
    cxplantillacontabilidad = models.CharField(max_length=10, blank=True, null=True)
    lcontabilizado = models.BooleanField(default= False)
    dcontabilizado = models.DateField(null= True)
    cxasientodiario = models.CharField(max_length=8, blank=True,null=True)
    nporcentajeiva = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.cxformapago
        
class Motivos_protesto_maestro(ClaseModelo):
    ctmotivoprotesto = models.TextField()
    ctabreviacion = models.CharField(max_length= 15) 
    lresponsabilidadgirador = models.BooleanField()

    def __str__(self):
        return self.ctabreviacion

class Notas_debito_cabecera(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('L', 'Liquidación'),
        ('C', 'Cobranza'),
        ('R', 'Recuperación'),
        ('B', 'Bancaria'),
        ('A', 'Ampliación de plazo'),
    )
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
    )
    dnotadebito = models.DateField()
    cxnotadebito = models.CharField(max_length=10, unique=True)
    cxtipofactoring = models.ForeignKey(Tipos_factoring, null=True
        ,to_field="cxtipofactoring", on_delete=models.CASCADE)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    cxestado = models.CharField(max_length=1, default="A") 
    nsaldo =  models.DecimalField(max_digits=10, decimal_places=2)
    # permitir nulo en los siguientes dos campos para registrar notas de debito
    # que no esten asociadas a alguna cobranza. Caso cuentas conjuntas
    cxtipooperacion = models.CharField(max_length=1, choices= TIPOS_DE_OPERACION
        ,null=True)
    operacion = models.BigIntegerField(null=True)

    def __str__(self):
        return self.cxnotadebito

class Notas_debito_detalle(ClaseModelo):
    notadebito = models.ForeignKey(Notas_debito_cabecera, on_delete=models.CASCADE)
    cargo = models.OneToOneField(Cargos_detalle, on_delete=models.RESTRICT)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Cheques_canjeados(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
        , related_name="cliente_canje"
    )
    accesoriooriginal = models.ForeignKey(ChequesAccesorios
        , on_delete= models.RESTRICT, related_name='cheque_original')
    accesorionuevo = models.ForeignKey(ChequesAccesorios
        , on_delete= models.RESTRICT, related_name='cheque_nuevo')
    ctmotivocanje = models.CharField(max_length=60)

class Ampliaciones_plazo_cabecera(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        ,to_field="cxcliente", on_delete=models.RESTRICT
    )
    dampliacionhasta =models.DateField()
    ncomision = models.DecimalField(max_digits=10, decimal_places=2)
    ndescuentodecartera = models.DecimalField(max_digits=10,
        decimal_places= 2, default= 0)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    notadedebito = models.OneToOneField(Notas_debito_cabecera
        , to_field="cxnotadebito", on_delete=models.CASCADE)

class Ampliaciones_plazo_detalle(ClaseModelo):
    TIPOS_ASIGNACION = (
        ('F', 'Factura pura'),
        ('A', 'Accesorio'),
    )
    ampliacion = models.ForeignKey(Ampliaciones_plazo_cabecera, on_delete=models.CASCADE)
    cxtipoasignacion = models.CharField( max_length=1, choices=TIPOS_ASIGNACION)
    documentoaccesorio = models.BigIntegerField()
    dampliaciondesde = models.DateField()
