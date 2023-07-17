from django.db import models
from bases.models import ClaseModelo
from pais.models import Bancos

# Create your models here.

class Clases_cliente(ClaseModelo):
    cxclase=models.CharField(max_length=3)

    def __str__(self):
        return self.cxclase

class Configuracion_correos(ClaseModelo):
    TIPOS_DE_CORREO = (
        ('FEL', 'FACTURACION ELECTRONICA'),
        ('CRM', 'CLIENTES'),
    )
    cxtipo=models.CharField(max_length=3,null=False, choices=TIPOS_DE_CORREO)
    ctservidorcorreosaliente =models.TextField(default= 'smtp.gmail.com')
    ctlogincorreo=models.TextField() ,
    ctpasswordcorreo=models.TextField() ,
    ctnombreremitente=models.CharField(max_length=60) ,
    ctasuntocorreo =models.TextField() ,
    npuerto =models.IntegerField(default= 587)

    def __str__(self):
        return '{} {}'.format(self.cxtipo,self.ctservidorcorreosaliente)

class Contador(ClaseModelo):
    cxtransaccion=models.CharField(max_length=20, null=False)
    nultimonumero=models.IntegerField(default=0)

class Cuentas_bancarias(ClaseModelo):
    cxbanco =models.OneToOneField(Bancos, on_delete=models.RESTRICT) 
    cxcuenta =models.CharField( max_length=20,null=False)
    ncheque =models.IntegerField(null=True)
    lformatopreimpreso =models.BooleanField(default=False)
    limprimecheque =models.BooleanField(default=False) 
    lactiva=models.BooleanField(default=True)
    ctrutaarchivobanco =models.TextField(null=True)
    cxciabco =models.CharField(max_length= 5, null=True) 

    def __str__(self):
        return '{} Cta.# {}'.format(self.cxbanco,self.cxcuenta)

class Datos_participantes(ClaseModelo):
    TIPOS_DE_ID = (
        ('C', 'CEDULA'),
        ('R', 'RUC'),
        ('P', 'PASAPORTE'),
        ('O', 'OTRO')
    )
    cxtipoid =models.CharField(max_length=1, null=False, choices=TIPOS_DE_ID)
    cxparticipante = models.CharField(max_length=13)
    ctnombre =models.CharField(max_length=100)
    cxzona =models.CharField(max_length=5, null=True)
    # cxlocalidad =models.CharField(max_length=4, null=True)
    cxestado =models.CharField(max_length=1, default='A')
    # cxpais =models.ForeignKey('Pais',to_field="cxpais", on_delete=models.CASCADE)
    ctdireccion =models.TextField(null=True)
    ctemail =models.EmailField(null=True)
    ctemail2 =models.EmailField(null=True, blank=True)
    cttelefono1 =models.CharField(max_length=30,null=True, blank=True)
    cttelefono2 =models.CharField(max_length=30,null=True, blank=True)
    ctcelular =models.CharField(max_length=30,null=True, blank=True)
    ctgirocomercial =models.TextField(null=True)
    cxactividad=models.CharField( max_length=10, null=True,
        help_text='actividad comercial segun código ciiu'    )
    dinicioactividades=models.DateField(null=True,
        help_text='fecha de inicio de actividades'    )

    def __str__(self):
        return self.ctnombre

    def save(self):
        self.ctnombre=self.ctnombre.upper()
        # self.ctobjetosocial=self.ctobjetosocial.upper()
        return super(Datos_participantes, self).save()

class Funcionarios(ClaseModelo):
    cxfuncionario = models.CharField(max_length=5)
    ctfuncionario = models.CharField(max_length=100)
    nporcentajecomision = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lcomisionflat = models.BooleanField()
    nperiocidadcomision = models.DecimalField(max_digits=5, decimal_places=2, default=360)
    lcomisionsobregao = models.BooleanField(default=False)
    lcomisionsobredescuentocartera = models.BooleanField(default=False)
    lcomisionsobrecartera = models.BooleanField(default=False)

    def __str__(self):
        return self.ctfuncionario

class Localidades(ClaseModelo):
    ctlocalidad = models.CharField(max_length=80, blank=True)
    lactiva = models.BooleanField(default=True)

    def __str__(self):
        return self.ctlocalidad

class Tasas_factoring(ClaseModelo):
    cxtasa = models.CharField(max_length=4)
    cttasa = models.CharField(max_length=60, blank=True)
    lflat = models.BooleanField(default=False)
    ndiasperiocidad = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    ctdescripcionenreporte = models.TextField(blank=True)
    limprimeenreporte = models.BooleanField(default=False)
    lcargaiva = models.BooleanField(default=True)
    lsobreanticipo = models.BooleanField(default=True)
    ctinicialesentablas = models.CharField(max_length=4,null=True)

    def __str__(self):
        return self.cttasa
    def save(self):
        self.cxtasa=self.cxtasa.upper()
        self.cttasa=self.cttasa.upper()
        return super(Tasas_factoring, self).save()
   
class Tipos_factoring(ClaseModelo):
    cxtipofactoring = models.CharField(max_length=3 , )
    cttipofactoring = models.CharField(max_length= 40) 
    ctabreviacion = models.CharField(max_length= 30) 
    cxmoneda = models.CharField(max_length=3) 
    nvalorminimopordocumento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    lmanejalineafactoring = models.BooleanField(default=  True)
    lanticipatotalnegociado = models.BooleanField(default= False)
    ndiasgracia  = models.IntegerField( default=5)
    lpermitediasferiados = models.BooleanField(default= False)
    lmanejacondicionesoperativas = models.BooleanField(default=True)
    lcargagaoa = models.BooleanField (default=True)
    lgeneradcenaceptacion = models.BooleanField(default= True)
    lgeneragaoenaceptacion = models.BooleanField(default= True)
    lesnegociada = models.BooleanField(default= True)
    lcobramorabc = models.BooleanField(default= False)
    nporcentajeretencionenfactura = models.DecimalField(max_digits = 5, decimal_places= 2, default=0, null=True)
    ctinicialesliquidacioncobranza = models.CharField(max_length=3, blank=True)
    lacumulagaoaatasagao = models.BooleanField(default= False)
    lfactoringproveedores = models.BooleanField(default= False)
    ctinicialesasignacion = models.CharField(max_length=3, blank=True, null=True)
    lcargadcenampliacionplazo = models.BooleanField(default= False)
    lgenerafacturaenaceptacion = models.BooleanField(default=True)
    
    def __str__(self):
        return self.ctabreviacion
    
    def save(self):
        self.ctinicialesliquidacioncobranza=self.ctinicialesliquidacioncobranza.upper()
        self.ctinicialesasignacion=self.ctinicialesasignacion.upper()
        self.cxtipofactoring=self.cxtipofactoring.upper()
        self.cttipofactoring=self.cttipofactoring.upper()
        return super(Tipos_factoring, self).save()

class Puntos_emision(ClaseModelo):
    cxestablecimiento = models.CharField(max_length=3)
    cxpuntoemision = models.CharField(max_length=3)
    ctdescripcion = models.CharField(max_length=30)
    ctdireccion = models.TextField()
    lgeneracionxmldocumentoelectronico = models.BooleanField(default=True)
    nultimasecuencia = models.IntegerField(default=0)
    lactiva = models.BooleanField(default=True)

    def __str__(self):
        return "{}-{}".format(self.cxestablecimiento, self.cxpuntoemision)

