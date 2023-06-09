from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Empresas(models.Model):
    ctruccompania = models.CharField(max_length=13, default='')
    ctnombre = models.CharField(max_length=60)
    lgratis = models.BooleanField(default=True)
    nmaximooperaciones = models.SmallIntegerField(default=10)
    lbloqueada = models.BooleanField(default=False)
    dcreacion = models.DateTimeField(auto_now_add=True)
    ctgerente = models.CharField(max_length=25, default='')
    ctdireccion = models.CharField(max_length=60, default='')
    ctcontribuyenteespecial = models.CharField(max_length= 4, default='0000')
    lregimenrimpe = models.BooleanField(default=False)
    dmodificacion = models.DateTimeField(auto_now=True)
    cxusuariomodifica = models.IntegerField(blank=True, null=True)
    ambientesri = models.CharField(max_length=1, default='1')
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

        