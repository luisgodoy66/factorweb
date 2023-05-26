from django.db import models

# Create your models here.
from bases.models import ClaseModelo
from empresa.models import Cuentas_bancarias, Tipos_factoring, Tasas_factoring

class Plan_cuentas(ClaseModelo):
    cxcuenta =  models.CharField( max_length=15)
    ctcuenta = models.TextField()
    nnivel = models.SmallIntegerField()
    ldetalle = models.BooleanField(default=False)

    def __str__(self):
        return '{} {}'.format(self.cxcuenta,self.ctcuenta)
    
class Cuentas_especiales(ClaseModelo):
    cuentaporcobrar = models.ForeignKey(Plan_cuentas,on_delete=models.RESTRICT
                                        , related_name='cuenta_cxc')
    pagoconcajachica =models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                        , related_name='cuenta_cajachica')
    sobrepago = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                  , related_name='cuenta_sobrepago')
    cuentaconjunta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                         , related_name='cuenta_cuentacompartida')
    protesto = models.ForeignKey(Plan_cuentas,on_delete=models.RESTRICT
                                 , related_name='cuenta_protesto')
    cuentaivaganado =models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT
                                         , related_name='cuenta_ivaganado')
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
    ctconcepto = models.TextField()
    nvalor = models.DecimalField(max_digits= 10,decimal_places= 2)
    # cxlocalidad character(2) COLLATE pg_catalog."default",
    dcontabilizado = models.DateField()

    def __str__(self):
        return self.ctconcepto

class Transaccion(ClaseModelo):
    cxcuenta = models.ForeignKey(Plan_cuentas, on_delete=models.CASCADE)
    cxtipo = models.CharField( max_length=1) 
    nvalor = models.DecimalField(max_digits= 10, decimal_places= 2)
    cxreferencia= models.CharField(max_length=30)
    dcontabilizado = models.DateField()
    cxtransaccion = models.CharField(max_length= 10)
    # norden = models.SmallIntegerField

class Cuentas_bancos(ClaseModelo):
    banco = models.OneToOneField(Cuentas_bancarias, on_delete=models.RESTRICT
                              , related_name="cuenta_banco")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT)

class Cuentas_tiposfactoring(ClaseModelo):
    tipofactoring = models.OneToOneField(Tipos_factoring, on_delete=models.RESTRICT
                                         , related_name="cuenta_tipofactoring")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT)

class Cuentas_tasasfactoring(ClaseModelo):
    tasafactoring = models.ForeignKey(Tasas_factoring, on_delete=models.RESTRICT
                                      , related_name="cuenta_tasafactoring")
    tipofactoring = models.ForeignKey(Tipos_factoring, on_delete=models.RESTRICT
                                      , related_name="cuenta_tasatipofactoring")
    cuenta = models.ForeignKey(Plan_cuentas, on_delete=models.RESTRICT)