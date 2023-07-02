from django.db import models

# Create your models here.
from bases.models import ClaseModelo
from empresa.models import Cuentas_bancarias, Tipos_factoring,  Puntos_emision
from clientes.models import Datos_generales
from operaciones.models import Documentos, ChequesAccesorios

class Plan_cuentas(ClaseModelo):
    cxcuenta =  models.CharField( max_length=15)
    ctcuenta = models.TextField()
    nnivel = models.SmallIntegerField()
    ldetalle = models.BooleanField(default=False)

    def __str__(self):
        return '{} {}'.format(self.cxcuenta,self.ctcuenta)

    def save(self):
        self.ctcuenta = self.ctcuenta.upper()
        super(Plan_cuentas, self).save()
  
    def activo_egreso(self):
        result = False
        nivel1 = self.cxcuenta[0]
        tipo = Cuentas_nivel1.objects.filter(cxcuenta = nivel1).first()
        if tipo:
            result = tipo.lactivo  or tipo.legreso
        return result
    
class Cuentas_especiales(ClaseModelo):
    pagoconcajachica =models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                        , related_name='cuenta_cajachica')
    sobrepago = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                  , null = True
                                  , related_name='cuenta_sobrepago')
    cuentaconjunta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                       , null = True
                                       , related_name='cuenta_cuentacompartida')
    protesto = models.ForeignKey(Plan_cuentas,on_delete=models.RESTRICT
                                 , null = True
                                 , related_name='cuenta_protesto')
    cuentaivaganado =models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                         , related_name='cuenta_ivaganado')
    ivadiferido =models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                   , null = True
                                   , related_name='cuenta_ivadiferido')
    cuentagananciaejercicio = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                                  , related_name='cuenta_ganancia')
    cuentaperdidaejercicio = models.ForeignKey(Plan_cuentas,on_delete=models.RESTRICT
                                                 , related_name='cuenta_perdida')
    cuentagananciaejercicioanterior = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                                          , related_name='cuenta_gananciaanterior')
    cuentaperdidaejercicioanterior = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                                         , related_name='cuenta_perdidaanterior')

class Diario_cabecera(ClaseModelo):
    cxtransaccion = models.CharField(max_length= 10) 
    dcontabilizado = models.DateField()
    ctconcepto = models.TextField()
    nvalor = models.DecimalField(max_digits= 10,decimal_places= 2)
    cxestado = models.CharField(max_length=1, default='A')
    # cxlocalidad character(2) COLLATE pg_catalog."default",

    def __str__(self):
        return self.ctconcepto

    def save(self):
        self.ctconcepto = self.ctconcepto.upper()
        super(Diario_cabecera, self).save()

class Transaccion(ClaseModelo):
    TIPOS=(
        ('D', 'Debe'),
        ('H', 'Haber')
    )
    diario = models.ForeignKey(Diario_cabecera, on_delete=models.CASCADE)
    cxcuenta = models.ForeignKey(Plan_cuentas, on_delete=models.CASCADE)
    cxtipo = models.CharField( max_length=1, choices=TIPOS) 
    ctreferencia= models.CharField(max_length=30)
    nvalor = models.DecimalField(max_digits= 10, decimal_places= 2)
    # norden = models.SmallIntegerField

class Cuentas_bancos(ClaseModelo):
    banco = models.OneToOneField(Cuentas_bancarias, on_delete=models.RESTRICT
                              , related_name="cuenta_banco")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT)

    def __str__(self):
        return self.cuenta

class Cuentas_tiposfactoring(ClaseModelo):
    tipofactoring = models.OneToOneField(Tipos_factoring, on_delete=models.RESTRICT
                                         , related_name="cuenta_tipofactoring")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT)
    cuentaporcobrar = models.ForeignKey(Plan_cuentas,on_delete=models.RESTRICT
                                        , related_name='cuenta_cxc')

    def __str__(self):
        return self.cuenta

from operaciones.models import Movimientos_maestro

class Cuentas_tasasfactoring(ClaseModelo):
    tasafactoring = models.ForeignKey(Movimientos_maestro, on_delete=models.RESTRICT
                                      , related_name="cuenta_tasafactoring")
    tipofactoring = models.ForeignKey(Tipos_factoring, on_delete=models.RESTRICT
                                      , related_name="cuenta_tasatipofactoring")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT)

    def __str__(self):
        return self.cuenta

class Cuentas_diferidos(ClaseModelo):
    tasafactoring = models.ForeignKey(Movimientos_maestro, on_delete=models.RESTRICT
                                      , related_name="cuentadiferido_tasafactoring")
    tipofactoring = models.ForeignKey(Tipos_factoring, on_delete=models.RESTRICT
                                      , related_name="cuentadiferido_tasatipofactoring")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                       , related_name="cuenta_diferido")
    def __str__(self):
        return self.cuentadiferido

class Cuentas_provisiones(ClaseModelo):
    tasafactoring = models.ForeignKey(Movimientos_maestro, on_delete=models.RESTRICT
                                      , related_name="cuentaprovision_tasafactoring")
    tipofactoring = models.ForeignKey(Tipos_factoring, on_delete=models.RESTRICT
                                      , related_name="cuentaprovision_tasatipofactoring")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                        , related_name="cuenta_provision")

    def __str__(self):
        return self.cuentaprovision

class Factura_venta(ClaseModelo):
    TIPOS_DE_OPERACION = (
        ('LA', 'Liquidación de asignación'),
        ('LC', 'Liquidación de cobranza'),
        ('AP', 'Ampliación de plazo'),
    )
    cliente = models.ForeignKey(Datos_generales, on_delete=models.RESTRICT)
    puntoemision = models.ForeignKey(Puntos_emision, on_delete=models.RESTRICT)
    cxnumerofactura = models.CharField(max_length=9)
    demision = models.DateField()
    cxestado = models.CharField(max_length=1, default='A')
    cxtipodocumento = models.CharField(max_length=2)
    nbasenoiva = models.DecimalField(max_digits=10, decimal_places=2)
    nbaseiva = models.DecimalField(max_digits=10, decimal_places=2)
    niva = models.DecimalField(max_digits=10, decimal_places=2)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2)
    nsaldo = models.DecimalField(max_digits=10, decimal_places=2)
    ldocumentoelectronicogenerado = models.BooleanField(default=False)
    nporcentajeiva = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    cxtipooperacion = models.CharField(max_length=2, choices= TIPOS_DE_OPERACION
        ,null=True)
    operacion = models.BigIntegerField(null=True)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_factura"
                                     , null=True)

    def __str__(self):
        return "{}-{}-{}".format(self.puntoemision.cxestablecimiento
                                 , self.puntoemision.cxpuntoemision, self.cxnumerofactura)

class Items_facturaventa(ClaseModelo):
    factura = models.ForeignKey(Factura_venta, on_delete=models.RESTRICT)
    item = models.ForeignKey(Movimientos_maestro, on_delete=models.RESTRICT)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2)
    lcargaiva = models.BooleanField()

    def __str__(self):
        return self.item
    
class Impuestos_facturaventa(ClaseModelo):
    factura = models.ForeignKey(Factura_venta, on_delete=models.RESTRICT)
    cximpuesto = models.CharField(max_length=3)
    cxporcentaje = models.CharField(max_length=5)
    nbase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
from clientes.models import  Cuenta_transferencia

class Comprobante_egreso(ClaseModelo):
    FORMAS_DE_PAGO = (
        ('EFE', 'Efectivo'),
        ('CHE', 'Cheque'),
        ('TRA', 'Transferencia'),
    )
    demision = models.DateField()
    cxestado = models.CharField(max_length=1, default='A')
    cxformapago = models.CharField(max_length=3, choices=FORMAS_DE_PAGO)
    cxbeneficiario = models.CharField(max_length=13, blank=True)
    ctrecibidopor = models.CharField(max_length=60)
    cxcuentapago = models.ForeignKey(Cuentas_bancarias, on_delete=models.RESTRICT
                                     , null=True)
    ctcheque = models.CharField(max_length=8, null=True)
    cxcuentadestino = models.ForeignKey(Cuenta_transferencia
        , on_delete=models.RESTRICT, null = True)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_egreso"
                                     , null=True)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Provisiones(ClaseModelo):
    cargo = models.ForeignKey(Movimientos_maestro, on_delete=models.RESTRICT)
    documento = models.ForeignKey(Documentos, on_delete=models.CASCADE)
    accesorio = models.ForeignKey(ChequesAccesorios, on_delete=models.CASCADE, null=True)
    nvalor = models.DecimalField(max_digits=10, decimal_places=2)
    lcontabilizado = models.BooleanField(default=False)
    asiento = models.OneToOneField(Diario_cabecera, on_delete=models.RESTRICT
                                     , related_name="asiento_provision"
                                     , null=True)
    año = models.CharField(max_length=4)
    mes = models.CharField(max_length=2)
    
class Control_meses(ClaseModelo):
    año = models.CharField(max_length=4)
    mes = models.CharField(max_length=2)
    lbloqueado = models.BooleanField(default=False)

class Saldos(ClaseModelo):
    cuenta = models.ForeignKey(Plan_cuentas, on_delete = models.RESTRICT)
    año = models.CharField(max_length=4)
    ndebe01 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe02 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe03 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe04 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe05 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe06 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe07 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe08 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe09 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe10 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe11 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe12 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber01 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber02 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber03 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber04 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber05 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber06 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber07 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber08 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber09 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber10 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber11 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber12 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe00 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber00 = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    ndebe = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
    nhaber = models.DecimalField(max_digits= 10, decimal_places= 2, default=0)
     
class Cuentas_nivel1(ClaseModelo):
    cxcuenta = models.CharField(max_length=1)
    descripcion = models.CharField(max_length=20)
    lactivo = models.BooleanField()
    lingreso = models.BooleanField()
    legreso = models.BooleanField()
    lorden = models.BooleanField()