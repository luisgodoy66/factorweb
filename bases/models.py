from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Empresas(models.Model):
    AMBIENTES_SRI = (
        ('1', 'Pruebas'),
        ('2', 'Producción'),
    )
    ctruccompania = models.CharField(max_length=13, default='', null=True)
    ctnombre = models.CharField(max_length=60, blank=True,)
    lgratis = models.BooleanField(default=True)
    nmaximooperaciones = models.SmallIntegerField(default=10)
    lbloqueada = models.BooleanField(default=False)
    dcreacion = models.DateTimeField(auto_now_add=True)
    ctgerente = models.CharField(max_length=25, default='', null=True)
    ctdireccion = models.CharField(max_length=60, default='', null=True)
    ctcontribuyenteespecial = models.CharField(max_length= 4, default='0000', null=True)
    lregimenrimpe = models.BooleanField(default=False)
    dmodificacion = models.DateTimeField(auto_now=True)
    cxusuariomodifica = models.IntegerField(blank=True, null=True)
    ambientesri = models.CharField(max_length=1, choices=AMBIENTES_SRI, default='1')
    ctciudad = models.CharField(max_length=20, default='')
    diniciooperaciones = models.DateField(null=True)
    dfinpruebas = models.DateField(null=True)
    ltipofactoringconfigurado= models.BooleanField(default=False)
    ltasasfactoringconfiguradas= models.BooleanField(default=False)
    ilogolargo = models.ImageField(null=True, upload_to='images/'
        , blank=True, default='logo1.png')
    ilogocorto = models.ImageField(null=True, upload_to='images/'
        , blank=True, default='logo2.png')
    nporcentajeiva = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    def __str__(self):
        return self.ctnombre
    
class ClaseModelo(models.Model):
    dregistro = models.DateTimeField(auto_now_add=True)
    dmodificacion = models.DateTimeField(auto_now=True)
    cxusuariocrea = models.ForeignKey(
        User, on_delete= models.CASCADE,
        related_name="%(app_label)s_%(class)s_usuariocrea",)
    cxusuariomodifica = models.IntegerField(blank=True, null=True)
    leliminado=models.BooleanField(default=False)
    cxusuarioelimina=models.IntegerField(blank=True,null=True)
    empresa =models.ForeignKey(Empresas,  on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_empresa",)
    
    class Meta:
        abstract=True

class Usuario_empresa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, 
                             related_name="usuario_empresa")
    empresa =models.ForeignKey(Empresas, on_delete=models.CASCADE,)

