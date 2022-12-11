from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ClaseModelo(models.Model):
    dregistro = models.DateTimeField(auto_now_add=True)
    dmodificacion = models.DateTimeField(auto_now=True)
    cxusuariocrea = models.ForeignKey(
        User, on_delete= models.CASCADE,
        related_name="%(app_label)s_%(class)s_usuariocrea",)
    cxusuariomodifica = models.IntegerField(blank=True, null=True)
    leliminado=models.BooleanField(default=False)
    cxusuarioelimina=models.IntegerField(blank=True,null=True)
    
    class Meta:
        abstract=True