from django.db import models

from bases.models import ClaseModelo
from empresa.models import Datos_participantes, Clases_cliente, Localidades
from pais.models import Bancos
from django.db.models import Sum, Q, F, ExpressionWrapper, DateField, CharField\

class Datos_compradores(ClaseModelo):
    ESTADOS_DE_COMPRADORES = (
        ('A', 'Activo'),
        ('X', 'Bloqueado'),
    )
    cxcomprador=models.OneToOneField(
        Datos_participantes, related_name="datos_generales_comprador"
        , on_delete=models.CASCADE )
    cxestado=models.CharField(max_length=1, default='A'
                              , choices=ESTADOS_DE_COMPRADORES )
    cxclase =models.ForeignKey(Clases_cliente, on_delete=models.DO_NOTHING 
                               ,null=True,)

    class Meta:
        ordering = [
            'cxcomprador__ctnombre'
            ]  

    def __str__(self):
        return self.cxcomprador.ctnombre
        
    def estado(self):
        return self.get_cxestado_display()

class Datos_generales_Manager(models.Manager):
        def clientes_nuevos_por_mes(self, id_empresa, año, mes):
            return self.filter(
                dprimeraoperacion__year=año,
                dprimeraoperacion__month=mes,
                cxcliente__empresa=id_empresa,
                leliminado = False,
            ).count()    

class Datos_generales(ClaseModelo):
    TIPOS_DE_CLIENTES = (
        ('N', 'Natural'),
        ('J', 'Jurídico'),
    )
    cxcliente=models.OneToOneField(
        Datos_participantes, related_name="datos_generales"
        , on_delete=models.CASCADE    )
    cxtipocliente=models.CharField(max_length=1, choices=TIPOS_DE_CLIENTES,
        help_text='tipo de cliente: natural , juridico, etc'    )
    dcontrato=models.DateField( null=True,
        help_text='Fecha de emisión de contrato'    )
    ctbeneficiariodevolucion=models.CharField(max_length=80, null=True,
        help_text='beneficiario de devolucion por valores no negociados'    )
    cxfuncionario=models.CharField(max_length=5, null=True,
        help_text='funcionario asignado'    )
    cxfuncionario2=models.CharField(max_length=5,null=True,
        help_text='funcionario que comparte la comision por venta'    )
    lcomisiones=models.BooleanField(default=True,
        help_text='el cliente ingresa en el proceso de calculo de comisiones a funconarios'    )
    npromediodemoradepago=models.DecimalField(max_digits=8, decimal_places=2, default=0,
        help_text='promedio general de cobro de documentos negociados'    )
    npromediodemoraderecuperacion=models.DecimalField(max_digits=8, decimal_places=2, default=0,
        help_text='promedio de recuperacion de documentos negociados protestados'    )
    ctemailfacturacionelectronica=models.EmailField(null=True,
        help_text='Dirección email para factracion electronica'    )
    cxreferidopor=models.CharField(max_length=4, null=True,
        help_text='codigo de freelancer que refiere'    )
    cxorigen=models.CharField(max_length=5,null=True,
        help_text='Código de localidad / oficina asignada del cliente'    )
    dprelegal=models.DateTimeField(null=True,
        help_text='fecha que cae en estado de pre legal'    )
    dlegal=models.DateTimeField(null=True,
        help_text='fecha que cae en estado de legal en proceso de envio a legal del sistema'    )
    cxlocalidad =models.ForeignKey(Localidades, on_delete=models.DO_NOTHING, null=True,
        help_text='Cree más sucursales en la opción Localidades del menú Configuración/Empresa'    )
    dprimeraoperacion=models.DateField(null=True,
        help_text='fecha de la primera operación'    )
    ncantidadoperaciones=models.SmallIntegerField(default=0,
        help_text='cantidad de operaciones realizadas'    )
    
    objects = Datos_generales_Manager()
    
    def __str__(self):
        return self.cxcliente.ctnombre

    class Meta:
        ordering = [
            'cxcliente__ctnombre'
            ]  
        
class Cuentas_bancarias(ClaseModelo):
    TIPOS_DE_CUENTAS = (
        ('A', 'Ahorro'),
        ('C', 'Corriente'),
    )
    TIPOS_DE_IDENTIFICACION=(
        ('C','Cédula'),
        ('R', 'RUC'),
        ('E','extranjero'),
    )
    cxparticipante=models.ForeignKey(Datos_participantes
        , on_delete=models.CASCADE
        , related_name="cuenta_bancaria")
    cxbanco = models.ForeignKey(Bancos, on_delete=models.RESTRICT
        , related_name="banco_cliente")
    cxtipocuenta=models.CharField(
        max_length=1, null=False, choices=TIPOS_DE_CUENTAS,
        help_text='A-ahorro / C-corriente'
    )
    cxcuenta=models.CharField(max_length=15,null=False,
        help_text='Número de cuenta'
    )
    lpropia=models.BooleanField(default=True)
    lactiva=models.BooleanField(default=True,)
    cxtipoidpropietario=models.CharField(max_length=1, null=True, blank=True
        ,choices=TIPOS_DE_IDENTIFICACION)
    cxidpropietario=models.CharField(max_length=13, null=True, blank=True)
    ctnombrepropietario=models.TextField(null=True, blank=True)

    def __str__(self):
        return '{} C.{}. N°{}'.format(self.cxbanco, self.cxtipocuenta,self.cxcuenta)

    def tipo_cuenta(self):
        return self.get_cxtipocuenta_display()
    
    def cuenta(self):
        return 'Cuenta {} Nº{}'.format(self.tipo_cuenta(),self.cxcuenta)
    
class Cuenta_transferencia_Manager(models.Manager):
    def cuenta_default(self, id_cliente):
        return self.filter(leliminado = False, cxcliente = id_cliente)

class Cuenta_transferencia(ClaseModelo):
    cxcliente=models.OneToOneField(Datos_generales
        , on_delete=models.CASCADE
        , related_name="cuenta_cliente")
    cxcuenta=models.OneToOneField(Cuentas_bancarias,
        on_delete=models.CASCADE
        , related_name="cuenta_transferencia")

    def __str__(self):
        return '{}-{}#{}'.format(self.cxcuenta.cxbanco
        ,self.cxcuenta.cxtipocuenta,self.cxcuenta.cxcuenta)

    objects= Cuenta_transferencia_Manager()

class Cupos_compradores(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales
        , on_delete=models.RESTRICT
        , related_name='comprador_cliente')
    cxcomprador = models.ForeignKey(Datos_compradores
        , on_delete=models.RESTRICT
        , related_name='comprador_comprador')
    cxmoneda = models.CharField(
        max_length=3, null=False,
        help_text='código de moneda',
    )
    daprobacion = models.DateTimeField(auto_now=True)
    ncupocartera=models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    nutilizadocartera=models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    cxtipocupo=models.CharField(max_length=1, null=True    )
    lactivo=models.BooleanField(default=True)
    lsenotifica=models.BooleanField(default=False)

    class Meta:
        ordering = [
            'cxcomprador__cxcomprador__ctnombre',
            'cxcliente__cxcliente__ctnombre'
            ]  

    def __str__(self):
        return self.cxcomprador.cxcomprador.ctnombre

    def disponible(self):
        return self.ncupocartera - self.nutilizadocartera

class Linea_Manager(models.Manager):
    def clientes_con_valores_pendientes(self, id_empresa, porcentaje=80):
        # Obtener el total de valores pendientes
        total_valores_pendientes = self.filter(
            leliminado=False, nutilizado__gt=0, empresa=id_empresa
        ).aggregate(total=Sum('nutilizado'))['total']

        if not total_valores_pendientes:
            return []

        # Calcular el porcentaje del total de valores pendientes
        total_por_ciento = total_valores_pendientes * porcentaje / 100

        # Obtener la lista de clientes con sus valores pendientes, ordenados en orden descendente
        clientes_valores_pendientes = self.filter(
            leliminado=False, nutilizado__gt=0, empresa=id_empresa
        ).values('cxcliente__cxcliente__ctnombre').annotate(
            total_pendiente=F('nutilizado')
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

class Linea_Factoring(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales
        , on_delete=models.RESTRICT
        , related_name="linea_factoring"
    )
    cxmoneda = models.CharField( max_length=3, null=False,
        help_text='código de moneda',    )
    nvalor=models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text='valor de linea otorgada en función del anticipo'    )
    nutilizado=models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text='total utilizado de la línea'    )
    cxexceso=models.CharField(max_length=6,
        help_text='Código de exceso temporal'    )
    nvalorexceso=models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text='valor de exceso temporal que suma al valor de la línea'    )
    lconrecurso = models.BooleanField(default=True)
    nreestructuracion=models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text='valor de reestructuracion'    )

    objects = Linea_Manager()

    def __str__(self):
        return self.cxcliente.ctnombre

    # def excede_monto_de_linea(self):
    #     return self.nvalor + self.nvalorexceso < self.nutilizado

    def disponible(self):
        return self.nvalor - self.nutilizado + self.nvalorexceso - self.nreestructuracion
    
    def porcentaje_disponible(self):
        return round( self.disponible() / self.nvalor * 100,2)

    def utilizado(self):
        return self.nutilizado + self.nreestructuracion
   
class Linea_factoring_hist(ClaseModelo):
    cxcliente=models.ForeignKey(Datos_generales
        , to_field="cxcliente", on_delete=models.RESTRICT
        , related_name="linea_factoring_hist"
    )
    cxmoneda = models.CharField( max_length=3, null=False,
        help_text='código de moneda',
    )
    nvalor=models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text='valor de linea otorgada en función del anticipo'
    )
    dcambio=models.DateField(help_text='fecha desde que rige el cambio'
    )

class Personas_juridicas(ClaseModelo):
    TIPOS_DE_EMPRESAS = (
        ('ANO', 'Anónima'),
        ('LTD', 'Responsabilidad Limitada'),
        ('SAS', 'Por acciones simplificadas'),
        ('COL', 'Nombre colectivo'),
        ('SIM', 'En comandita simple'),
        ('MIX', 'Economía mixta'),
    )
    TIPOS_DE_ESTADO_CIVIL = (
        ('S', 'Soltero'),
        ('C', 'Casado'),
        ('U', 'unión libre'),
        ('D', 'Divorciado')
    )
    cxcliente = models.OneToOneField(Datos_participantes,
        on_delete=models.CASCADE,
        related_name="persona_juridica")
    ctnombrecorto = models.TextField( blank=True, help_text='nombre de fantasia')
    cxtipoempresa = models.CharField( max_length=3
        , help_text='Anonima, limitada, etc.', choices=TIPOS_DE_EMPRESAS)
    ctcontacto = models.TextField()
    ladministrasocios=models.BooleanField(null=False)
    ladministraindividual =models.BooleanField(null=False)
    ctobjetosocial=models.TextField( default='',
        help_text='objeto social de la actividad del cliente')
    cxrepresentante1 = models.CharField( max_length=13, null=False
        , help_text='id de representante legal' )
    ctrepresentante1 = models.TextField( null=False
        , help_text='Nombre de representante')
    dvencimientocargorepresentante1=  models.DateField(null=False)
    ctcargorepresentante1 = models.CharField( max_length=60)
    cxestadocivilrepresentante1 = models.CharField( max_length=3
        , null=True, choices=TIPOS_DE_ESTADO_CIVIL)
    cttelefonorepresentante1 = models.CharField(max_length=20)
    cxrepresentante2 = models.CharField( max_length=13, null=True
        , blank=True)
    ctrepresentante2 = models.TextField( null=True, blank=True
        ,help_text='Nombre de segundo representante')
    dvencimientocargorepresentante2=models.DateField(null=True
        , blank=True)
    ctcargorepresentante2 = models.CharField( max_length=60
        , null=True, blank=True)
    cxestadocivilrepresentante2 = models.CharField(max_length=3
        , null=True, choices=TIPOS_DE_ESTADO_CIVIL, blank=True)
    cttelefonorepresentante2 = models.CharField( max_length=20
        , null=True, blank=True)
    cxrepresentante3 = models.CharField( max_length=13, null=True
        , blank=True)
    ctrepresentante3 = models.TextField(null=True, blank=True)
    dvencimientocargorepresentante3 = models.DateField(null=True
        , blank=True)
    ctcargorepresentante3 = models.CharField( max_length=60
        , null=True, blank=True)
    cxestadocivilrepresentante3 = models.CharField(max_length=3
    , null=True, choices=TIPOS_DE_ESTADO_CIVIL, blank=True)
    cttelefonorepresentante3 = models.CharField( max_length=20
        , null=True, blank=True)
    

    def __str__(self):
        return self.cxcliente.ctnombre

    def save(self):
        self.ctnombrecorto=self.ctnombrecorto.upper()
        # self.ctobjetosocial=self.ctobjetosocial.upper()
        return super(Personas_juridicas, self).save()

class Personas_naturales(ClaseModelo):
    TIPOS_DE_SEXOS = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )
    TIPOS_DE_ESTADO_CIVIL=(
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V','Viudo'),
        ('D','Divorciado'),
        ('U','Unión libre')
    )
    cxcliente = models.ForeignKey(Datos_participantes, on_delete=models.CASCADE)
    dnacimiento=models.DateField(null=True, default="2000-01-01")
    cxsexo = models.CharField(max_length=1, choices=TIPOS_DE_SEXOS, null=False)
    cxestadocivil = models.CharField( max_length=3, choices=TIPOS_DE_ESTADO_CIVIL) 
    cxconyuge =models.CharField( max_length=10, blank=True) 
    ctnombrenegocio=models.CharField(max_length=60) 
    ctnombreconyuge =models.CharField(max_length=60, blank=True) 
    ctprofesion =models.CharField(max_length=60)  

    def __str__(self):
        return self.ctnombrenegocio

    def save(self):
        self.ctnombrenegocio=self.ctnombrenegocio.upper()
        return super(Personas_naturales, self).save()

class Socios(ClaseModelo):
    cxcliente = models.ForeignKey(Datos_participantes,
        on_delete=models.CASCADE)
    cxsocio=models.CharField( max_length=13, null=False)
    ctsocio=models.TextField(null=False)
    ncapitalaportado=models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    nporcentajeparticipacion=models.DecimalField(
        max_digits=5, decimal_places=2, null=False
    )

    def __str__(self):
        return self.ctsocio

class Datos_operativos_hist(ClaseModelo):
    ESTADOS_DE_CLIENTES = (
        ('A', 'Activo'),
        ('B', 'Baja'),
        ('I', 'Inactivo'),
        ('P', 'Pre legal'),
        ('L', 'Legal'),
        ('X', 'Bloqueado'),
    )
    cxcliente=models.ForeignKey(Datos_generales, on_delete=models.RESTRICT
        , related_name="datos_operativos_hist")
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

    def estado(self):
        return self.get_cxestado_display()
    
