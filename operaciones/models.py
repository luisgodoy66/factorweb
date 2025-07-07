from random import choices
from django.db import models
from django.forms import BooleanField
from django.db.models import Sum, Q, F, ExpressionWrapper, DateField, CharField\
    , Value, Count, IntegerField, DecimalField
from django.db.models.functions import Cast, ExtractDay
from django.db.models.functions import Concat
from django.utils.dateparse import parse_date

from bases.models import ClaseModelo
from empresa.models import Clases_cliente, Tipos_factoring, Cuentas_bancarias\
    , Movimientos_maestro
from clientes.models import Datos_generales as Datos_generales_cliente\
    , Cuenta_transferencia, Datos_compradores
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
        , on_delete=models.RESTRICT
        , related_name="datos_operativos"
    )
    dalta = models.DateTimeField(auto_created=True) 
    cxtipoliquidacioncobranza = models.CharField(max_length=1, default="L", null=True) 
    cxclase =models.ForeignKey(Clases_cliente, on_delete=models.DO_NOTHING)
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
    ntasamora= models.DecimalField(max_digits=11, decimal_places=8, default=0) 

    def __str__(self):
        return self.cxcliente.cxcliente.ctnombre
  
    def estado(self):
        return self.get_cxestado_display()
    
class Asignacion_manager(models.Manager):
    def operaciones_negociadas(self, id_empresa, año):
        # en django obtener el año del campo date llamado ddesembolso?
        return self.filter(ddesembolso__year = año,
            cxestado = "P"
            , leliminado = False
            , empresa = id_empresa)\
            .aggregate(enero = Sum('nvalor', filter=Q(ddesembolso__month=1))
                       , febrero= Sum('nvalor', filter=Q(ddesembolso__month=2))
                       , marzo= Sum('nvalor', filter=Q(ddesembolso__month=3))
                       , abril= Sum('nvalor', filter=Q(ddesembolso__month=4))
                       , mayo= Sum('nvalor', filter=Q(ddesembolso__month=5))
                       , junio= Sum('nvalor', filter=Q(ddesembolso__month=6))
                       , julio= Sum('nvalor', filter=Q(ddesembolso__month=7))
                       , agosto= Sum('nvalor', filter=Q(ddesembolso__month=8))
                       , septiembre= Sum('nvalor', filter=Q(ddesembolso__month=9))
                       , octubre= Sum('nvalor', filter=Q(ddesembolso__month=10))
                       , noviembre= Sum('nvalor', filter=Q(ddesembolso__month=11))
                       , diciembre= Sum('nvalor', filter=Q(ddesembolso__month=12))
                       )
    
    def operaciones_negociadas_cliente(self, id_empresa, año, id_cliente):
        # en django obtener el año del campo date llamado ddesembolso?
        return self.filter(ddesembolso__year = año,
            cxestado = "P"
            , leliminado = False
            , empresa = id_empresa
            , cxcliente = id_cliente)\
            .aggregate(enero = Sum('nvalor', filter=Q(ddesembolso__month=1))
                       , febrero= Sum('nvalor', filter=Q(ddesembolso__month=2))
                       , marzo= Sum('nvalor', filter=Q(ddesembolso__month=3))
                       , abril= Sum('nvalor', filter=Q(ddesembolso__month=4))
                       , mayo= Sum('nvalor', filter=Q(ddesembolso__month=5))
                       , junio= Sum('nvalor', filter=Q(ddesembolso__month=6))
                       , julio= Sum('nvalor', filter=Q(ddesembolso__month=7))
                       , agosto= Sum('nvalor', filter=Q(ddesembolso__month=8))
                       , septiembre= Sum('nvalor', filter=Q(ddesembolso__month=9))
                       , octubre= Sum('nvalor', filter=Q(ddesembolso__month=10))
                       , noviembre= Sum('nvalor', filter=Q(ddesembolso__month=11))
                       , diciembre= Sum('nvalor', filter=Q(ddesembolso__month=12))
                       )
    
    def total_negociado(self, id_empresa):
        return self.filter(cxestado = "P"
                           , leliminado = False
                           , empresa = id_empresa)\
            .aggregate(Total = Sum('nvalor'))

    def total_por_actividad(self, id_empresa):
        return self.filter(cxestado="P",
                           leliminado=False,
                           empresa=id_empresa)\
            .values('cxcliente__cxcliente__actividad__ctactividad')\
            .annotate(total=Sum('nvalor'))\
            .order_by('cxcliente__cxcliente__actividad__ctactividad')

    def negociaciones_por_mes(self, id_empresa, año, mes):
        return self.filter(
            ddesembolso__year=año,
            ddesembolso__month=mes,
            cxestado="P",
            leliminado=False,
            empresa=id_empresa
        ).values('ddesembolso').annotate(
            cantidad=Count('id'),
            total_monto=Sum('nvalor')
        ).order_by('ddesembolso')

class Asignacion(ClaseModelo):
    TIPOS_DE_ASIGNACION = (
        ('A', 'Con accesorios'),
        ('F', 'Facturas puras'),
    )
    ESTADOS_DE_ASIGNACION = (
        ('L', 'Liquidada'),
        ('P', 'Pagada'),
    )
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.CASCADE
        , related_name="cliente_asignacion"
    )
    cxasignacion = models.CharField(max_length=8 ) 
    cxtipofactoring = models.ForeignKey(Tipos_factoring
        , on_delete=models.RESTRICT
        , related_name="tipofactoring_asignacion")
    cxtipo = models.CharField(max_length=1, choices=TIPOS_DE_ASIGNACION) 
    cxmodalidadfactoring = models.CharField(max_length=1) 
    cxlocalidad = models.CharField(max_length=4, blank=True) 
    dnegociacion = models.DateTimeField(auto_created=True) 
    ddesembolso= models.DateField(auto_created=True) 
    nvalor = models.DecimalField(max_digits=15, decimal_places =2) 
    nanticipo = models.DecimalField(max_digits=10, decimal_places= 2, default=0)
    # cxexcesolineafactoring = models.CharField(max_length=6) 
    cxestado = models.CharField(max_length=1, default="L", choices=ESTADOS_DE_ASIGNACION) 
    ctbancochequegarantia = models.CharField(max_length=25, blank=True, null=True) 
    ctcuentachequegarantia = models.CharField(max_length=15, blank=True, null=True) 
    ctnumerochequegarantia = models.CharField(max_length=7, blank=True, null=True) 
    dchequegaratia = models.DateTimeField(auto_created=True, null=True) 
    ngao = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    ndescuentodecartera = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    notroscargos = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    nbaseiva = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    nbasenoiva = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    jotroscargos = models.JSONField(blank=True, null=True)
    ctinstrucciondepago = models.TextField(blank=True)
    nretencionenfactura = models.DecimalField(max_digits=10, decimal_places= 2, default= 0)
    lcartacesiongenerada = models.BooleanField(default=False, null=True) 
    nmayorplazonegociacion = models.SmallIntegerField(default=0, )
    lfacturagenerada = models.BooleanField(default=False)
    nporcentajeiva = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    lanexosimpresos= models.BooleanField(default=False)
    
    objects = Asignacion_manager()

    def __str__(self):
        return self.cxasignacion

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
    
class Documentos_Manager(models.Manager):
    def facturas_pendientes(self, fecha_corte, id_empresa):
        fecha = parse_date(fecha_corte)
        return self.filter(dvencimiento__lte = fecha - F('ndiasprorroga')
                , leliminado = False, nsaldo__gt = 0
                , empresa = id_empresa
                , cxasignacion__in = Asignacion.objects
                    .filter(cxtipo = "F", cxestado = "P", leliminado = False))\
                    .order_by('dvencimiento')

    def facturas_pendientes_vencimiento_original(self, fecha_corte, id_empresa):
        # no considera la prorroga
        fecha = parse_date(fecha_corte)
        return self.filter(dvencimiento__lte = fecha 
                , leliminado = False, nsaldo__gt = 0
                , empresa = id_empresa
                , cxasignacion__in = Asignacion.objects
                    .filter(cxtipo = "F", cxestado = "P", leliminado = False))\
                    .order_by('dvencimiento')

    def antigüedad_cartera(self, id_empresa):
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
            , cxasignacion__leliminado = False
            , empresa = id_empresa)\
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
    
    def antigüedad_por_cliente(self, id_empresa):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , cxasignacion__cxtipo = "F"
            , cxasignacion__cxestado = "P"
            , cxasignacion__leliminado = False
            , empresa = id_empresa)\
            .values('cxcliente__cxcliente__ctnombre')\
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

    def TotalCartera(self, id_empresa):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , empresa = id_empresa
                           , cxasignacion__cxestado = "P"
                           , cxasignacion__leliminado = False)\
            .aggregate(Total = Sum('nsaldo'))

    def cartera_pendiente(self, id_empresa):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , cxasignacion__in = Asignacion.objects
                    .filter(cxtipo = "F", cxestado = "P"
                            , empresa = id_empresa
                            , leliminado = False))\
                    .values("cxcomprador__cxcomprador__ctnombre"
                            ,"cxcliente__cxcliente__ctnombre"
                            , "cxasignacion__cxasignacion"
                            , "ctdocumento"
                            , "dvencimiento", "ndiasprorroga"
                            , "cxasignacion__ddesembolso"
                            , "nsaldo")\
                    .annotate(vencimiento = ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                              , output_field=DateField()),
                            dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                            dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                            )\
                    .order_by('cxcliente__cxcliente__ctnombre')
    
    def TotalCarteraCliente(self, id_cliente):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , cxasignacion__cxcliente = id_cliente
                           , cxasignacion__cxestado = "P"
                           , cxasignacion__leliminado = False)\
            .aggregate(Total = Sum('nsaldo'))
    
    def clientes_con_valores_pendientes(self, id_empresa, porcentaje=80):
        # Obtener el total de valores pendientes
        total_valores_pendientes = self.filter(
            leliminado=False, nsaldo__gt=0, empresa=id_empresa
        ).aggregate(total=Sum('nsaldo'))['total']

        if not total_valores_pendientes:
            return []

        # Calcular el porcentaje del total de valores pendientes
        total_por_ciento = total_valores_pendientes * porcentaje / 100

        # Obtener la lista de clientes con sus valores pendientes, ordenados en orden descendente
        clientes_valores_pendientes = self.filter(
            leliminado=False, nsaldo__gt=0, empresa=id_empresa
        ).values('cxcliente__cxcliente__ctnombre').annotate(
            total_pendiente=Sum('nsaldo')
        ).order_by('-total_pendiente')

        # Iterar sobre los clientes acumulando sus valores pendientes hasta alcanzar el porcentaje del total
        acumulado = 0
        clientes_por_ciento = []
        otros_total = 0
        otros_cantidad = 0

        for cliente in clientes_valores_pendientes:
            if acumulado >= total_por_ciento:
                otros_total += cliente['total_pendiente']
                otros_cantidad +=1
            else:
                clientes_por_ciento.append(cliente)
                acumulado += cliente['total_pendiente']

        if otros_total > 0:
            clientes_por_ciento.append({
                'cxcliente__cxcliente__ctnombre': 'OTROS CLIENTES ' 
                    + '(' + str(otros_cantidad) + ') CON EL '
                    + str(100 - porcentaje) + '% ' 
                    ,
                'total_pendiente': otros_total
            })

        return clientes_por_ciento
        
    def revision_cartera(self, id_empresa):
        vcdo30 = datetime.today() + timedelta(days=-30)
        vcdo60 = datetime.today() + timedelta(days=-60)

        return self.filter(leliminado=False, nsaldo__gt=0,
                   cxasignacion__cxtipo="F",
                   cxasignacion__cxestado="P",
                   cxasignacion__leliminado=False,
                   empresa=id_empresa) \
            .values('cxcliente__cxcliente__ctnombre',
                'cxcliente__linea_factoring__nvalor',
                'cxcliente__datos_operativos__cxclase__cxclase',
                'cxcliente__datos_operativos__cxestado',
                'cxcliente',
                ) \
            .annotate(
            vencido_mas_60=Sum('nsaldo', filter=Q(dvencimiento__lt=vcdo60)),
            vencido_60=Sum('nsaldo', filter=Q(dvencimiento__lt=vcdo30, dvencimiento__gte=vcdo60)),
            vencido_30=Sum('nsaldo', filter=Q(dvencimiento__lt=datetime.today(), dvencimiento__gte=vcdo30)),
            por_vencer=Sum('nsaldo', filter=Q(dvencimiento__gte=datetime.today())),
            protesto=Value(0, output_field=DecimalField()),
            total=Sum('nsaldo')
            ) \
            .order_by()

class Documentos(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.CASCADE
        , related_name="cliente_documento"
    )
    cxasignacion=models.ForeignKey(Asignacion
        , on_delete=models.CASCADE
    )
    cxtipofactoring=models.ForeignKey(Tipos_factoring
        , on_delete=models.CASCADE
        , related_name="tipo_factoring"
    )
    nreferencia = models.BigIntegerField(null=True)  
    cxcomprador=models.ForeignKey(Datos_compradores
        , on_delete=models.CASCADE
        , related_name="comprador"
    )
    # cxtipodocumento=models.ForeignKey(Tipos_documentos
    #     , on_delete=models.CASCADE
    #     , related_name="tipo_documento"
    # )
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
    ncontadorprorrogas = models.SmallIntegerField(default=0)
    lfacturagenerada = models.BooleanField(default=False)
    cxautorizacion_ec = models.CharField(max_length=49, null=True)

    objects= Documentos_Manager()

    def __str__(self):
        return self.ctdocumento

    def dias_vencidos(self):
        return (date.today() - self.dvencimiento)/timedelta(days=1)

    def dias_negociados(self):
        return (self.dvencimiento - self.cxasignacion.ddesembolso)/timedelta(days=1)

    def vencimiento(self):
        return self.dvencimiento + timedelta(days=self.ndiasprorroga)

    def total_cargos(self):
        return self.ngao + self.ndescuentocartera
    
class ChequesAccesorios_Manager(models.Manager):

    def cheques_a_depositar(self, fecha_corte, id_empresa):
        fecha = parse_date(fecha_corte)
        return self.filter(dvencimiento__lte = fecha - F('ndiasprorroga')
                , cxestado = 'A'
                , leliminado = False, lcanjeado = False
                , laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa
                )

    def facturas_pendientes(self, fecha_corte, id_empresa):
        fecha = parse_date(fecha_corte)
        return self.filter(
                dvencimiento__lte = fecha - F('ndiasprorroga'),
                laccesorioquitado = True, chequequitado__cxestado = 'A'
                , leliminado = False, lcanjeado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa
                )

    def facturas_pendientes_vencimiento_original(self, fecha_corte, id_empresa):
        # no considera la prorroga
        fecha = parse_date(fecha_corte)
        return self.filter(
                dvencimiento__lte = fecha ,
                laccesorioquitado = True, chequequitado__cxestado = 'A'
                , leliminado = False, lcanjeado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa
                )

    def antigüedad_cartera(self, id_empresa):
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
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
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

    def antigüedad_por_cliente(self, id_empresa):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False, lcanjeado  = False, laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre')\
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

    def cartera_pendiente(self, id_empresa):
        return self.filter(laccesorioquitado = True
                           , chequequitado__cxestado = 'A'
                           , leliminado = False, lcanjeado = False
                           , empresa = id_empresa
                           , documento__cxasignacion__cxestado = "P"
                           , documento__cxasignacion__leliminado = False)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                        , "chequequitado__nsaldo")\
                .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                         , output_field = DateField() ),
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('documento__cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                        )\
                .order_by('documento__cxcliente__cxcliente__ctnombre')

    def cheques_pendientes(self, id_empresa):
        return self.filter(laccesorioquitado = False
                           , cxestado='A'
                           , leliminado = False, lcanjeado = False
                           , empresa = id_empresa
                           , documento__cxasignacion__cxestado = "P"
                           , documento__cxasignacion__leliminado = False)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                        , "ntotal")\
                .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                         , output_field = DateField() ),
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('documento__cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                        descripcion =  Concat('cxbanco__ctbanco'
                                                , Value(' CTA.') 
                                                , 'ctcuenta'
                                                , Value(' CH/')
                                                , ('ctcheque'), output_field=CharField())
                          )\
                .order_by('documento__cxcliente__cxcliente__ctnombre')

    def cheques_pendientes_cliente(self, id_cliente):
        return self.filter(laccesorioquitado = False, cxestado='A'
                , leliminado = False, lcanjeado = False
                , documento__cxcliente = id_cliente
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                        , "ntotal")\
                .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                         , output_field = DateField() ),
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('documento__cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                        descripcion =  Concat('cxbanco__ctbanco'
                                                , Value(' CTA.') 
                                                , 'ctcuenta'
                                                , Value(' CH/')
                                                , ('ctcheque'), output_field=CharField())
                          )\
                .order_by('documento__cxcliente__cxcliente__ctnombre')

    def revision_cartera(self, id_empresa):
        vcdo30 = datetime.today() + timedelta(days=-30)
        vcdo60 = datetime.today() + timedelta(days=-60)

        return self.filter(cxestado = 'A'
                , leliminado = False, lcanjeado  = False, laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre',
                    'documento__cxcliente__linea_factoring__nvalor',
                    'documento__cxcliente__datos_operativos__cxclase__cxclase',
                    'documento__cxcliente__datos_operativos__cxestado',
                    'documento__cxcliente',
                    ) \
            .annotate(
                vencido_mas_60=Sum('ntotal', filter=Q(dvencimiento__lt=vcdo60)),
                vencido_60=Sum('ntotal', filter=Q(dvencimiento__lt=vcdo30, dvencimiento__gte=vcdo60)),
                vencido_30=Sum('ntotal', filter=Q(dvencimiento__lt=datetime.today()
                    , dvencimiento__gte=vcdo30)),
                por_vencer=Sum('ntotal', filter=Q(dvencimiento__gte=datetime.today())),
                protesto=Value(0, output_field=DecimalField()),
                total=Sum('ntotal')
            ) \
            .order_by()

class Cheques_quitados_Manager(models.Manager):
    def antigüedad_cartera(self, id_empresa):
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
                , accesorio_quitado__documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
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

    def antigüedad_por_cliente(self, id_empresa):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False
                , accesorio_quitado__documento__cxasignacion__cxestado = "P"
                , accesorio_quitado__documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
            .values('accesorio_quitado__documento__cxcliente__cxcliente__ctnombre')\
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

    def revision_cartera(self, id_empresa):
        vcdo30 = datetime.today() + timedelta(days=-30)
        vcdo60 = datetime.today() + timedelta(days=-60)

        return self.filter(cxestado = 'A'
                , leliminado = False
                , accesorio_quitado__documento__cxasignacion__cxestado = "P"
                , accesorio_quitado__documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
            .values('accesorio_quitado__documento__cxcliente__cxcliente__ctnombre',
                    'accesorio_quitado__documento__cxcliente__linea_factoring__nvalor',
                    'accesorio_quitado__documento__cxcliente__datos_operativos__cxclase__cxclase',
                    'accesorio_quitado__documento__cxcliente__datos_operativos__cxestado',
                    'accesorio_quitado__documento__cxcliente',
                    ) \
            .annotate(
                vencido_mas_60=Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt=vcdo60)),
                vencido_60=Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt=vcdo30
                    , accesorio_quitado__dvencimiento__gte=vcdo60)),
                vencido_30=Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt=datetime.today()
                    , accesorio_quitado__dvencimiento__gte=vcdo30)),
                por_vencer=Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gte=datetime.today())),
                protesto=Value(0, output_field=DecimalField()),
                total=Sum('nsaldo')
            ) \
            .order_by()

class Cheques_quitados(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT
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
    ndiasprorroga= models.SmallIntegerField(default=0, null=True)
    ncontadorprorrogas = models.SmallIntegerField(default=0)
    
    objects= ChequesAccesorios_Manager()

    def __str__(self):
        return '{} CTA.{} CH/{}'.format(self.cxbanco,self.ctcuenta, self.ctcheque)

    def dias_vencidos(self):
        return (date.today() - self.dvencimiento)/timedelta(days=1)

    def vencimiento(self):
        return self.dvencimiento + timedelta(days=self.ndiasprorroga)

    def total_cargos(self):
        return self.ngao + self.ndescuentocartera
    
class Movimientos_clientes(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT
        , related_name="movimientos"
    )
    cxtipofactoring = models.BigIntegerField(null=True) 
    cxmovimiento = models.ForeignKey(Movimientos_maestro, on_delete=models.CASCADE
                                     , related_name="maestro_movimientos", null=True) 
    nvalor = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    cxoperacion = models.CharField(max_length=10) 
    dmovimiento = models.DateField() 
    
    def __str__(self):
        return self.cxcliente

class Cargos_detalle(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT, related_name="cargos"
    )
    cxtipofactoring = models.BigIntegerField(null=True) 
    cxasignacion = models.ForeignKey(Asignacion, on_delete=models.RESTRICT
        , null=True) 
    cxdocumento  = models.ForeignKey(Documentos, on_delete=models.RESTRICT
        , null=True)  
    cxmovimiento = models.ForeignKey(Movimientos_maestro, on_delete=models.RESTRICT
                                     ,related_name='cargo_movimiento', null=True)
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
        , on_delete=models.CASCADE)
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
    TIPOS_DE_CLIENTES = (
        ('N', 'Natural'),
        ('J', 'Jurídico'),
        ('T', 'Todos'),
    )
    ctnombre = models.TextField()
    lactivo = models.BooleanField(default=True)
    fanexo = models.FileField(upload_to='anexos/', blank=True, )
    cxtipocliente=models.CharField(max_length=1, choices=TIPOS_DE_CLIENTES,
        help_text='tipo de cliente: natural , jurídico, todos', default='J')
    lcesionfacturas = models.BooleanField(default=False)
    
    def __str__(self):
        return self.ctnombre
    
    def tipo_cliente(self):
        return dict(self.TIPOS_DE_CLIENTES).get(self.cxtipocliente, 'Todos')
        
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
        ('F', 'Factural al vencimiento'), 
    )
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT
    )
    dnotadebito = models.DateField()
    cxnotadebito = models.CharField(max_length=10)
    cxtipofactoring = models.ForeignKey(Tipos_factoring, null=True
        , on_delete=models.CASCADE)
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
    
    def origen(self):
        if (self.cxtipooperacion == "A"):
            ap = Ampliaciones_plazo_cabecera.objects.filter(pk=self.operacion).first()
            return ap.__str__()
        else:
        # if (self.cxtipooperacion == "L"):
        #     ap = Liquidacion_cabecera.objects.filter(pk=self.operacion).first()
        #     return ap.__str__()
        # if (self.cxtipooperacion == "C"):
        #     ap = Documentos_cabecera.objects.filter(pk=self.operacion).first()
        #     return ap.__str__()
        # if (self.cxtipooperacion == "R"):
        #     ap = Recuperaciones_cabecera.objects.filter(pk=self.operacion).first()
        #     return ap.__str__()
            if (self.cxtipooperacion == "B"):
                return 'Cargo efectuado por el banco'
            else:
                return self.operacion

class Notas_debito_detalle(ClaseModelo):
    notadebito = models.ForeignKey(Notas_debito_cabecera, on_delete=models.CASCADE)
    cargo = models.OneToOneField(Cargos_detalle, on_delete=models.RESTRICT)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Cheques_canjeados(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT
        , related_name="cliente_canje"
    )
    accesoriooriginal = models.ForeignKey(ChequesAccesorios
        , on_delete= models.RESTRICT, related_name='cheque_original')
    accesorionuevo = models.ForeignKey(ChequesAccesorios
        , on_delete= models.RESTRICT, related_name='cheque_nuevo')
    ctmotivocanje = models.CharField(max_length=60)

class Ampliaciones_plazo_cabecera(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT
    )
    dampliacionhasta =models.DateField()
    ncomision = models.DecimalField(max_digits=10, decimal_places=2)
    ndescuentodecartera = models.DecimalField(max_digits=10,
        decimal_places= 2, default= 0)
    niva = models.DecimalField(max_digits=10,decimal_places= 2, default= 0)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notadebito = models.OneToOneField(Notas_debito_cabecera
        ,related_name="ampliacion_notadedebito", on_delete=models.CASCADE)
    lfacturagenerada = models.BooleanField(default=False)
    nporcentajeiva = models.DecimalField(max_digits=5, decimal_places=2, default=12)

    def __str__(self):
        return self.notadebito.cxnotadebito
    
class Ampliaciones_plazo_detalle(ClaseModelo):
    TIPOS_ASIGNACION = (
        ('F', 'Factura pura'),
        ('A', 'Accesorio'),
    )
    ampliacion = models.ForeignKey(Ampliaciones_plazo_cabecera, on_delete=models.CASCADE)
    cxtipoasignacion = models.CharField( max_length=1, choices=TIPOS_ASIGNACION)
    documentoaccesorio = models.BigIntegerField()
    dampliaciondesde = models.DateField()
    nvalorcartera= models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def plazo(self):
        return (self.ampliacion.dampliacionhasta - self.dampliaciondesde)/timedelta(days=1)

from contabilidad.models import Diario_cabecera

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
    cxcliente = models.ForeignKey(Datos_generales_cliente, on_delete=models.RESTRICT)
    nvalor =  models.DecimalField(max_digits=10, decimal_places=2)
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxcuentapago = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
        , null = True, blank=True)
    cxbeneficiario = models.CharField(max_length=13, blank=True, null=True)
    ctbeneficiario = models.TextField(blank=True, null=True)
    cxcuentadestino = models.ForeignKey(Cuenta_transferencia
        , on_delete=models.RESTRICT, null = True)
    lgeneradoarchivobanco = models.BooleanField(default=False)
    lcontabilizado = models.BooleanField(default= False)
    cxasiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_desembolso"
                                     , null=True)

    def __str__(self):
        return self.cxformapago

class Pagares_Manager(models.Manager):

    def TotalPagaresCliente(self, id_cliente):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , cxcliente = id_cliente)\
            .aggregate(Total = Sum('nsaldo'))
    
    def TotalPagares(self, id_empresa):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , empresa = id_empresa
                           )\
            .aggregate(Total = Sum('nsaldo'))

class Pagares(ClaseModelo):
    cxpagare = models.CharField(max_length=8 ) 
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.CASCADE
        , related_name="cliente_pagare"
    )
    demision = models.DateField(auto_created=True) 
    dvencimiento = models.DateField()
    ncapital = models.DecimalField(max_digits=15, decimal_places =2) 
    ninteres = models.DecimalField(max_digits=15, decimal_places =2)
    nsaldo = models.DecimalField(max_digits=15, decimal_places =2)
    cxestado = models.CharField(max_length=1, default="A", ) 
    ntasainteres = models.DecimalField(max_digits=5, decimal_places=2)
    nplazo = models.IntegerField()
    ncantidadcuotas = models.IntegerField()
    dultimacobranza = models.DateTimeField(null=True) 

    objects = Pagares_Manager()

    def __str__(self):
        return self.cxpagare

    def valor_total(self):
        return self.ncapital + self.ninteres
    
    def tasa_porciento(self):
        return self.ntasainteres*100
    
class Cuotas_pagare_Manager(models.Manager):
    
    def cuotas_pendientes(self, fecha_corte, id_empresa):
        fecha = parse_date(fecha_corte)
        return self.filter(dfechapago__lte = fecha # - F('ndiasprorroga')
                , leliminado = False, nsaldo__gt = 0
                , empresa = id_empresa)

    def antigüedad_cartera(self, id_empresa):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , pagare__leliminado = False
            , empresa = id_empresa)\
            .aggregate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo60
                    , dfechapago__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo30
                    , dfechapago__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(dfechapago__lt = datetime.today()
                    , dfechapago__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(dfechapago__gte = datetime.today()
                    , dfechapago__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(dfechapago__gt = xver30
                    , dfechapago__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver60
                    , dfechapago__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver90) ) 
                )
    
    def antigüedad_por_cliente(self, id_empresa):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , pagare__leliminado = False
            , empresa = id_empresa)\
            .values('pagare__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo60
                    , dfechapago__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo30
                    , dfechapago__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(dfechapago__lt = datetime.today()
                    , dfechapago__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(dfechapago__gte = datetime.today()
                    , dfechapago__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(dfechapago__gt = xver30
                    , dfechapago__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver60
                    , dfechapago__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver90) ) 
                , total = Sum('nsaldo')
                )\
            .order_by()

    def revision_cartera(self, id_empresa):
        vcdo30 = datetime.today() + timedelta(days=-30)
        vcdo60 = datetime.today() + timedelta(days=-60)

        return self.filter(leliminado = False, nsaldo__gt = 0
            , pagare__leliminado = False
            , empresa = id_empresa)\
            .values('pagare__cxcliente__cxcliente__ctnombre',
                    'pagare__cxcliente__linea_factoring__nvalor',
                    'pagare__cxcliente__datos_operativos__cxclase__cxclase',
                    'pagare__cxcliente__datos_operativos__cxestado',
                    'pagare__cxcliente',
                    ) \
            .annotate(
                vencido_mas_60=Sum('nsaldo', filter=Q(dfechapago__lt=vcdo60)),
                vencido_60=Sum('nsaldo', filter=Q(dfechapago__lt=vcdo30, dfechapago__gte=vcdo60)),
                vencido_30=Sum('nsaldo', filter=Q(dfechapago__lt=datetime.today()
                    , dfechapago__gte=vcdo30)),
                por_vencer=Sum('nsaldo', filter=Q(dfechapago__gte=datetime.today())),
                protesto = Value(0, output_field=DecimalField()),
                total=Sum('nsaldo')
            ) \
            .order_by()

class Pagare_detalle(ClaseModelo):
    pagare = models.ForeignKey(Pagares, on_delete=models.CASCADE)
    ncuota = models.SmallIntegerField()
    dfechapago = models.DateField()
    ninteres = models.DecimalField(max_digits=15, decimal_places=2)
    ncapital = models.DecimalField(max_digits=15, decimal_places=2)
    nsaldo = models.DecimalField(max_digits=15, decimal_places=2)
    nsaldointeres = models.DecimalField(max_digits=15, decimal_places=2)
    dultimacobranza = models.DateTimeField(null=True) 
    cxestado = models.CharField(max_length=1, default="A") 

    objects = Cuotas_pagare_Manager()

    def __str__(self):
        return "# {}".format(self.ncuota)
    
    def valor_cuota(self):
        return self.ncapital + self.ninteres

    def dias_vencidos(self):
        return (date.today() - self.dfechapago)/timedelta(days=1)

    class Meta:
        ordering = [
            'ncuota'
            ]  

class Revision_cartera(ClaseModelo):
    TIPOS_DE_PARTICIPANTE = (
        ('C', 'Cliente'),
        ('D', 'Deudor'),
    )

    drevision = models.DateField()
    cxtipoparticipante = models.CharField(max_length=1, default='C',
                                          choices=TIPOS_DE_PARTICIPANTE)

    def __str__(self):
        return self.dregistro.strftime('%A, %d de %B %H:%M')

class Revision_cartera_detalle(ClaseModelo):
    revision = models.ForeignKey(Revision_cartera, on_delete=models.CASCADE)
    cxcliente = models.ForeignKey(Datos_generales_cliente, on_delete=models.RESTRICT)
    nvencido30 = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    nvencido60 = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    nvencidomas60 = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    nvencido90 = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    nvencidomas90 = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    nporvencer = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    nprotesto = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    nlineaactual = models.DecimalField(max_digits=15, decimal_places=2, default=0,null=True)
    ctclaseactual = models.CharField(max_length=3, null=True)
    ctestadoactual = models.CharField(max_length=1, null=True)
    ctcomentario = models.TextField()

class Cortes_historico(ClaseModelo):
    ctdescripcion = models.CharField(max_length=60)
    lactivo = models.BooleanField(default=True)

    def __str__(self):
        return self.ctdescripcion

class Documentos_historico_Manager(models.Manager):
    # def facturas_pendientes(self, fecha_corte, id_empresa):
    #     fecha = parse_date(fecha_corte)
    #     return self.filter(dvencimiento__lte = fecha - F('ndiasprorroga')
    #             , leliminado = False, nsaldo__gt = 0
    #             , empresa = id_empresa
    #             , cxasignacion__in = Asignacion.objects
    #                 .filter(cxtipo = "F", cxestado = "P", leliminado = False))\
    #                 .order_by('dvencimiento')

    # def facturas_pendientes_vencimiento_original(self, fecha_corte, id_empresa):
    #     # no considera la prorroga
    #     fecha = parse_date(fecha_corte)
    #     return self.filter(dvencimiento__lte = fecha 
    #             , leliminado = False, nsaldo__gt = 0
    #             , empresa = id_empresa
    #             , cxasignacion__in = Asignacion.objects
    #                 .filter(cxtipo = "F", cxestado = "P", leliminado = False))\
    #                 .order_by('dvencimiento')

    def antigüedad_cartera(self, id_empresa, id_corte):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                           , nsaldo__gt = 0, historico = id_corte
                            , cxasignacion__cxtipo = "F"
                            , cxasignacion__cxestado = "P"
                            , cxasignacion__leliminado = False
                            , empresa = id_empresa)\
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
    
    def antigüedad_por_cliente(self, id_empresa, id_corte):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , cxasignacion__cxtipo = "F"
            , historico = id_corte
            , cxasignacion__cxestado = "P"
            , cxasignacion__leliminado = False
            , empresa = id_empresa)\
            .values('cxcliente__cxcliente__ctnombre')\
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

    def TotalCartera(self, id_empresa, id_corte):
        return self.filter(leliminado = False, nsaldo__gt = 0
                           , historico = id_corte
                           , empresa = id_empresa
                           , cxasignacion__cxestado = "P"
                           , cxasignacion__leliminado = False)\
            .aggregate(Total = Sum('nsaldo'))

    def cartera_pendiente(self, id_empresa, id_corte):
        return self.filter(leliminado = False, nsaldo__gt = 0
                            , historico = id_corte
                           , cxasignacion__in = Asignacion.objects
                    .filter(cxtipo = "F", cxestado = "P"
                            , empresa = id_empresa
                            , leliminado = False))\
                    .values("cxcomprador__cxcomprador__ctnombre"
                            ,"cxcliente__cxcliente__ctnombre"
                            , "cxasignacion__cxasignacion"
                            , "ctdocumento"
                            , "dvencimiento", "ndiasprorroga"
                            , "cxasignacion__ddesembolso"
                            , "nsaldo")\
                    .annotate(vencimiento = ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                              , output_field=DateField()),
                            dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                            dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                            )\
                    .order_by('cxcliente__cxcliente__ctnombre')
    
    # def TotalCarteraCliente(self, id_cliente):
    #     return self.filter(leliminado = False, nsaldo__gt = 0
    #                        , cxasignacion__cxcliente = id_cliente
    #                        , cxasignacion__cxestado = "P"
    #                        , cxasignacion__leliminado = False)\
    #         .aggregate(Total = Sum('nsaldo'))
    
    # def clientes_con_valores_pendientes(self, id_empresa, porcentaje=80):
    #     # Obtener el total de valores pendientes
    #     total_valores_pendientes = self.filter(
    #         leliminado=False, nsaldo__gt=0, empresa=id_empresa
    #     ).aggregate(total=Sum('nsaldo'))['total']

    #     if not total_valores_pendientes:
    #         return []

    #     # Calcular el porcentaje del total de valores pendientes
    #     total_por_ciento = total_valores_pendientes * porcentaje / 100

    #     # Obtener la lista de clientes con sus valores pendientes, ordenados en orden descendente
    #     clientes_valores_pendientes = self.filter(
    #         leliminado=False, nsaldo__gt=0, empresa=id_empresa
    #     ).values('cxcliente__cxcliente__ctnombre').annotate(
    #         total_pendiente=Sum('nsaldo')
    #     ).order_by('-total_pendiente')

    #     # Iterar sobre los clientes acumulando sus valores pendientes hasta alcanzar el porcentaje del total
    #     acumulado = 0
    #     clientes_por_ciento = []
    #     otros_total = 0
    #     otros_cantidad = 0

    #     for cliente in clientes_valores_pendientes:
    #         if acumulado >= total_por_ciento:
    #             otros_total += cliente['total_pendiente']
    #             otros_cantidad +=1
    #         else:
    #             clientes_por_ciento.append(cliente)
    #             acumulado += cliente['total_pendiente']

    #     if otros_total > 0:
    #         clientes_por_ciento.append({
    #             'cxcliente__cxcliente__ctnombre': 'OTROS CLIENTES ' 
    #                 + '(' + str(otros_cantidad) + ') CON EL '
    #                 + str(100 - porcentaje) + '% ' 
    #                 ,
    #             'total_pendiente': otros_total
    #         })

    #     return clientes_por_ciento
        
    # def revision_cartera(self, id_empresa):
    #     vcdo30 = datetime.today() + timedelta(days=-30)
    #     # xver30 = datetime.today() + timedelta(days=30)

    #     return self.filter(leliminado=False, nsaldo__gt=0,
    #                cxasignacion__cxtipo="F",
    #                cxasignacion__cxestado="P",
    #                cxasignacion__leliminado=False,
    #                empresa=id_empresa) \
    #         .values('cxcliente__cxcliente__ctnombre',
    #             'cxcliente__linea_factoring__nvalor',
    #             'cxcliente__datos_operativos__cxclase__cxclase',
    #             'cxcliente__datos_operativos__cxestado',
    #             'cxcliente',
    #             ) \
    #         .annotate(
    #         vencido_mas_30=Sum('nsaldo', filter=Q(dvencimiento__lt=vcdo30)),
    #         vencido_30=Sum('nsaldo', filter=Q(dvencimiento__lt=datetime.today(), dvencimiento__gte=vcdo30)),
    #         por_vencer=Sum('nsaldo', filter=Q(dvencimiento__gte=datetime.today())),
    #         protesto=Value(0, output_field=DecimalField()),
    #         total=Sum('nsaldo')
    #         ) \
    #         .order_by()

class Documentos_historico(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.CASCADE
        , related_name="cliente_documento_historico"
    )
    cxasignacion=models.ForeignKey(Asignacion
        , on_delete=models.CASCADE
    )
    cxtipofactoring=models.ForeignKey(Tipos_factoring
        , on_delete=models.CASCADE
        , related_name="tipo_factoring_historico"
    )
    nreferencia = models.BigIntegerField(null=True)  
    cxcomprador=models.ForeignKey(Datos_compradores
        , on_delete=models.CASCADE
        , related_name="comprador_documento_historico"
    )
    # cxtipodocumento=models.ForeignKey(Tipos_documentos
    #     , on_delete=models.CASCADE
    #     , related_name="tipo_documento"
    # )
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
    ncontadorprorrogas = models.SmallIntegerField(default=0)
    lfacturagenerada = models.BooleanField(default=False)
    cxautorizacion_ec = models.CharField(max_length=49, null=True)
    historico = models.ForeignKey(Cortes_historico, on_delete=models.CASCADE
        , related_name="documento_historico")

    objects= Documentos_historico_Manager()

    def __str__(self):
        return self.ctdocumento

    def dias_vencidos(self):
        return (date.today() - self.dvencimiento)/timedelta(days=1)

    def dias_negociados(self):
        return (self.dvencimiento - self.cxasignacion.ddesembolso)/timedelta(days=1)

    def vencimiento(self):
        return self.dvencimiento + timedelta(days=self.ndiasprorroga)

    def total_cargos(self):
        return self.ngao + self.ndescuentocartera
    
class Cheques_quitados_historico_Manager(models.Manager):
    def antigüedad_cartera(self, id_empresa, id_corte):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False
                , historico = id_corte
                , accesorio_quitado_historico__documento__cxasignacion__cxestado = "P"
                , accesorio_quitado_historico__documento__cxasignacion__leliminado = False
                , accesorio_quitado_historico__historico = id_corte
                , empresa = id_empresa)\
            .aggregate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = vcdo60
                    , accesorio_quitado_historico__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = vcdo30
                    , accesorio_quitado_historico__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = datetime.today()
                    , accesorio_quitado_historico__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gte = datetime.today()
                    , accesorio_quitado_historico__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gt = xver30
                    , accesorio_quitado_historico__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gt = xver60
                    , accesorio_quitado_historico__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gt = xver90) ) 
                )

    def antigüedad_por_cliente(self, id_empresa, id_corte):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False
                , historico = id_corte
                , accesorio_quitado_historico__documento__cxasignacion__cxestado = "P"
                , accesorio_quitado_historico__documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
            .values('accesorio_quitado_historico__documento__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = vcdo60
                    , accesorio_quitado_historico__dvencimiento__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = vcdo30
                    , accesorio_quitado_historico__dvencimiento__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__lt = datetime.today()
                    , accesorio_quitado_historico__dvencimiento__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gte = datetime.today()
                    , accesorio_quitado_historico__dvencimiento__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gt = xver30
                    , accesorio_quitado_historico__dvencimiento__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gt = xver60
                    , accesorio_quitado_historico__dvencimiento__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(accesorio_quitado_historico__dvencimiento__gt = xver90) ) 
                , total = Sum('nsaldo')
                )

    # def revision_cartera(self, id_empresa):
    #     vcdo30 = datetime.today() + timedelta(days=-30)
    #     # xver30 = datetime.today() + timedelta(days=30)

    #     return self.filter(cxestado = 'A'
    #             , leliminado = False
    #             , accesorio_quitado__documento__cxasignacion__cxestado = "P"
    #             , accesorio_quitado__documento__cxasignacion__leliminado = False
    #             , empresa = id_empresa)\
    #         .values('accesorio_quitado__documento__cxcliente__cxcliente__ctnombre',
    #                 'accesorio_quitado__documento__cxcliente__linea_factoring__nvalor',
    #                 'accesorio_quitado__documento__cxcliente__datos_operativos__cxclase__cxclase',
    #                 'accesorio_quitado__documento__cxcliente__datos_operativos__cxestado',
    #                 'accesorio_quitado__documento__cxcliente',
    #                 ) \
    #         .annotate(
    #             vencido_mas_30=Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt=vcdo30)),
    #             vencido_30 = Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__lt = datetime.today()
    #                 , accesorio_quitado__dvencimiento__gte = vcdo30)),
    #             por_vencer=Sum('nsaldo', filter=Q(accesorio_quitado__dvencimiento__gte=datetime.today())),
    #             protesto=Value(0, output_field=DecimalField()),
    #             total=Sum('nsaldo')
    #         ) \
    #         .order_by()

class Cheques_quitados_historico(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales_cliente
        , on_delete=models.RESTRICT
    )
    cxestado = models.CharField(max_length=1, default="A") 
    nsaldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ctmotivoquitado = models.CharField(max_length=60)
    dultimacobranza = models.DateTimeField(null=True) 
    historico = models.ForeignKey(Cortes_historico, on_delete=models.CASCADE
        , related_name="cheque_quitado_historico")
    idanterior = models.BigIntegerField()
            
    objects = Cheques_quitados_historico_Manager()

class ChequesAccesorios_historico_Manager(models.Manager):

    # def cheques_a_depositar(self, fecha_corte, id_empresa):
    #     fecha = parse_date(fecha_corte)
    #     return self.filter(dvencimiento__lte = fecha - F('ndiasprorroga')
    #             , cxestado = 'A'
    #             , leliminado = False, lcanjeado = False
    #             , laccesorioquitado = False
    #             , documento__cxasignacion__cxestado = "P"
    #             , documento__cxasignacion__leliminado = False
    #             , empresa = id_empresa
    #             )

    # def facturas_pendientes(self, fecha_corte, id_empresa):
    #     fecha = parse_date(fecha_corte)
    #     return self.filter(
    #             dvencimiento__lte = fecha - F('ndiasprorroga'),
    #             laccesorioquitado = True, chequequitado__cxestado = 'A'
    #             , leliminado = False, lcanjeado = False
    #             , documento__cxasignacion__cxestado = "P"
    #             , documento__cxasignacion__leliminado = False
    #             , empresa = id_empresa
    #             )

    # def facturas_pendientes_vencimiento_original(self, fecha_corte, id_empresa):
    #     # no considera la prorroga
    #     fecha = parse_date(fecha_corte)
    #     return self.filter(
    #             dvencimiento__lte = fecha ,
    #             laccesorioquitado = True, chequequitado__cxestado = 'A'
    #             , leliminado = False, lcanjeado = False
    #             , documento__cxasignacion__cxestado = "P"
    #             , documento__cxasignacion__leliminado = False
    #             , empresa = id_empresa
    #             )

    def antigüedad_cartera(self, id_empresa, id_corte):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False, lcanjeado  = False
                , historico = id_corte
                , laccesorioquitado = False
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
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

    def antigüedad_por_cliente(self, id_empresa, id_corte):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter(cxestado = 'A'
                , leliminado = False, lcanjeado  = False
                , laccesorioquitado = False
                , historico = id_corte
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False
                , empresa = id_empresa)\
            .values('documento__cxcliente__cxcliente__ctnombre')\
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

    def cartera_pendiente(self, id_empresa, id_corte):
        return self.filter(laccesorioquitado = True
                           , chequequitado__cxestado = 'A'
                           , chequequitado__historico = id_corte
                           , leliminado = False, lcanjeado = False
                            , historico = id_corte
                           , empresa = id_empresa
                           , documento__cxasignacion__cxestado = "P"
                           , documento__cxasignacion__leliminado = False)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                        , "chequequitado__nsaldo")\
                .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                         , output_field = DateField() ),
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('documento__cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                        )\
                .order_by('documento__cxcliente__cxcliente__ctnombre')

    def cheques_pendientes(self, id_empresa, id_corte):
        return self.filter(laccesorioquitado = False
                           , cxestado='A'
                            , historico = id_corte
                           , leliminado = False, lcanjeado = False
                           , empresa = id_empresa
                           , documento__cxasignacion__cxestado = "P"
                           , documento__cxasignacion__leliminado = False)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                        , "ntotal")\
                .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                         , output_field = DateField() ),
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('documento__cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
                        descripcion =  Concat('cxbanco__ctbanco'
                                                , Value(' CTA.') 
                                                , 'ctcuenta'
                                                , Value(' CH/')
                                                , ('ctcheque'), output_field=CharField())
                          )\
                .order_by('documento__cxcliente__cxcliente__ctnombre')

    # def cheques_pendientes_cliente(self, id_cliente):
    #     return self.filter(laccesorioquitado = False, cxestado='A'
    #             , leliminado = False, lcanjeado = False
    #             , documento__cxcliente = id_cliente
    #             , documento__cxasignacion__cxestado = "P"
    #             , documento__cxasignacion__leliminado = False)\
    #             .values("documento__cxcomprador__cxcomprador__ctnombre"
    #                     , "documento__cxcliente__cxcliente__ctnombre"
    #                     , "documento__cxasignacion__cxasignacion"
    #                     , "documento__ctdocumento"
    #                     , "dvencimiento", "ndiasprorroga"
    #                     , "documento__cxasignacion__ddesembolso"
    #                     , "ntotal")\
    #             .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
    #                                                      , output_field = DateField() ),
    #                     dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
    #                                                                         , output_field=DateField()))
    #                                             , IntegerField()),
    #                     dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
    #                                                                       -F('documento__cxasignacion__ddesembolso')
    #                                                                       , output_field=DateField()))
    #                                             , IntegerField()),
    #                     descripcion =  Concat('cxbanco__ctbanco'
    #                                             , Value(' CTA.') 
    #                                             , 'ctcuenta'
    #                                             , Value(' CH/')
    #                                             , ('ctcheque'), output_field=CharField())
    #                       )\
    #             .order_by('documento__cxcliente__cxcliente__ctnombre')

    # def revision_cartera(self, id_empresa):
    #     vcdo30 = datetime.today() + timedelta(days=-30)
    #     # xver30 = datetime.today() + timedelta(days=30)

    #     return self.filter(cxestado = 'A'
    #             , leliminado = False, lcanjeado  = False, laccesorioquitado = False
    #             , documento__cxasignacion__cxestado = "P"
    #             , documento__cxasignacion__leliminado = False
    #             , empresa = id_empresa)\
    #         .values('documento__cxcliente__cxcliente__ctnombre',
    #                 'documento__cxcliente__linea_factoring__nvalor',
    #                 'documento__cxcliente__datos_operativos__cxclase__cxclase',
    #                 'documento__cxcliente__datos_operativos__cxestado',
    #                 'documento__cxcliente',
    #                 ) \
    #         .annotate(
    #             vencido_mas_30=Sum('ntotal', filter=Q(dvencimiento__lt=vcdo30)),
    #             vencido_30 = Sum('ntotal', filter=Q(dvencimiento__lt = datetime.today()
    #                 , dvencimiento__gte = vcdo30)),
    #             por_vencer=Sum('ntotal', filter=Q(dvencimiento__gte=datetime.today())),
    #             protesto=Value(0, output_field=DecimalField()),
    #             total=Sum('ntotal')
    #         ) \
    #         .order_by()

class ChequesAccesorios_historico(ClaseModelo):
    PROPIETARIO = (
        ('C', 'Cliente'),
        ('D', 'Deudor'),
    )
    cxpropietariocuenta = models.CharField(max_length=1, choices= PROPIETARIO
        , default='D')
    documento = models.ForeignKey(Documentos
        , on_delete=models.CASCADE, related_name="documento_cheque_historico")
    cxbanco = models.ForeignKey(Bancos, on_delete=models.RESTRICT
        , related_name="banco_cheque_operacion_historico")
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
    chequequitado = models.ForeignKey(Cheques_quitados_historico, null=True
        , on_delete=models.RESTRICT, related_name="accesorio_quitado_historico")
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
    ndiasprorroga= models.SmallIntegerField(default=0, null=True)
    ncontadorprorrogas = models.SmallIntegerField(default=0)
    historico= models.ForeignKey(Cortes_historico, on_delete=models.CASCADE
        , related_name="cheque_accesorio_historico")
    
    objects= ChequesAccesorios_historico_Manager()

    def __str__(self):
        return '{} CTA.{} CH/{}'.format(self.cxbanco,self.ctcuenta, self.ctcheque)

    def dias_vencidos(self):
        return (date.today() - self.dvencimiento)/timedelta(days=1)

    def vencimiento(self):
        return self.dvencimiento + timedelta(days=self.ndiasprorroga)

    def total_cargos(self):
        return self.ngao + self.ndescuentocartera
    
class Cuotas_pagare_historico_Manager(models.Manager):
    
    # def cuotas_pendientes(self, fecha_corte, id_empresa):
    #     fecha = parse_date(fecha_corte)
    #     return self.filter(dfechapago__lte = fecha # - F('ndiasprorroga')
    #             , leliminado = False, nsaldo__gt = 0
    #             , empresa = id_empresa)

    def antigüedad_cartera(self, id_empresa, id_corte):
        # grafico de antigüedad de cartera 
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False, nsaldo__gt = 0
            , pagare__leliminado = False
            , historico = id_corte
            , empresa = id_empresa)\
            .aggregate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo60
                    , dfechapago__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo30
                    , dfechapago__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(dfechapago__lt = datetime.today()
                    , dfechapago__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(dfechapago__gte = datetime.today()
                    , dfechapago__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(dfechapago__gt = xver30
                    , dfechapago__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver60
                    , dfechapago__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver90) ) 
                )
    
    def antigüedad_por_cliente(self, id_empresa, id_corte):
        vcdo90 = datetime.today()+timedelta(days=-90)
        vcdo60 = datetime.today()+timedelta(days=-60)
        vcdo30 = datetime.today()+timedelta(days=-30)
        xver30 = datetime.today()+timedelta(days=30)
        xver60 = datetime.today()+timedelta(days=60)
        xver90 = datetime.today()+timedelta(days=90)

        return self.filter( leliminado = False
                           , historico = id_corte
                           , nsaldo__gt = 0
                            , pagare__leliminado = False
                            , empresa = id_empresa)\
            .values('pagare__cxcliente__cxcliente__ctnombre')\
            .annotate(
                vencido_mas_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo90) ) 
                , vencido_90 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo60
                    , dfechapago__gte = vcdo90))
                , vencido_60 = Sum('nsaldo', filter=Q(dfechapago__lt = vcdo30
                    , dfechapago__gte = vcdo60))
                , vencido_30 = Sum('nsaldo', filter=Q(dfechapago__lt = datetime.today()
                    , dfechapago__gte = vcdo30))
                ,porvencer_30 = Sum('nsaldo', filter=Q(dfechapago__gte = datetime.today()
                    , dfechapago__lte = xver30))
                ,porvencer_60 = Sum('nsaldo', filter=Q(dfechapago__gt = xver30
                    , dfechapago__lte = xver60))
                ,porvencer_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver60
                    , dfechapago__lte = xver90))
                , porvencer_mas_90 = Sum('nsaldo', filter=Q(dfechapago__gt = xver90) ) 
                , total = Sum('nsaldo')
                )\
            .order_by()

    # def revision_cartera(self, id_empresa):
    #     vcdo30 = datetime.today() + timedelta(days=-30)
    #     # xver30 = datetime.today() + timedelta(days=30)

    #     return self.filter(leliminado = False, nsaldo__gt = 0
    #         , pagare__leliminado = False
    #         , empresa = id_empresa)\
    #         .values('pagare__cxcliente__cxcliente__ctnombre',
    #                 'pagare__cxcliente__linea_factoring__nvalor',
    #                 'pagare__cxcliente__datos_operativos__cxclase__cxclase',
    #                 'pagare__cxcliente__datos_operativos__cxestado',
    #                 'pagare__cxcliente',
    #                 ) \
    #         .annotate(
    #             vencido_mas_30=Sum('nsaldo', filter=Q(dfechapago__lt=vcdo30)),
    #             vencido_30 = Sum('nsaldo', filter=Q(dfechapago__lt = datetime.today()
    #                 , dfechapago__gte = vcdo30)),
    #             por_vencer=Sum('nsaldo', filter=Q(dfechapago__gte=datetime.today())),
    #             protesto = Value(0, output_field=DecimalField()),
    #             total=Sum('nsaldo')
    #         ) \
    #         .order_by()

    def TotalPagares(self, id_empresa, id_corte):
        return self.filter(leliminado = False, nsaldo__gt = 0
                            , historico = id_corte
                           , empresa = id_empresa
                           )\
            .aggregate(Total = Sum('nsaldo'))

class Pagare_detalle_historico(ClaseModelo):
    pagare = models.ForeignKey(Pagares, on_delete=models.CASCADE)
    ncuota = models.SmallIntegerField()
    dfechapago = models.DateField()
    ninteres = models.DecimalField(max_digits=15, decimal_places=2)
    ncapital = models.DecimalField(max_digits=15, decimal_places=2)
    nsaldo = models.DecimalField(max_digits=15, decimal_places=2)
    nsaldointeres = models.DecimalField(max_digits=15, decimal_places=2)
    dultimacobranza = models.DateTimeField(null=True) 
    cxestado = models.CharField(max_length=1, default="A") 
    historico= models.ForeignKey(Cortes_historico, on_delete=models.CASCADE
        , related_name="cuota_historico")

    objects = Cuotas_pagare_historico_Manager()

    def __str__(self):
        return "# {}".format(self.ncuota)
    
    def valor_cuota(self):
        return self.ncapital + self.ninteres

    def dias_vencidos(self):
        return (date.today() - self.dfechapago)/timedelta(days=1)

    class Meta:
        ordering = [
            'ncuota'
            ]  

