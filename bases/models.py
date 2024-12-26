from django.db import models
from django.contrib.auth.models import User
# from django.utils import timezone
# from django.utils.http import urlquote
# from django.utils.translation import ugettext_lazy as _
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin\
#     , BaseUserManager

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
    ilogolargo = models.ImageField(null=True, upload_to='factorweb/images/logo/'
        , blank=True, default='logo1.png')
    ilogocorto = models.ImageField(null=True, upload_to='factorweb/images/logo/'
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

# class UsuarioManager(BaseUserManager):
#     def _create_user(self, username, password, email,**extra_fields):

#         if not username and not email :
#             raise ValueError('Debe ingresar nombre de usuario e email.')
#         if len (username)>80:
#             raise Exception ("El nombre de usuario debe tener menos de 80 caracteres ")
#         # if extra_fields.get("is_superuser"):
#         #     raise TypeError("'is_superuser' is a reserved name for internal use.")
#         # if 'password' in extra_fields:
#         #     raise TypeError('"password" should not be used as a field. Use "set_password()" instead.')
        
#         # Normalize the address by lowercasing it.
#         email = self.normalize_email(email)

#         user = self.model(username=username 
#                           , email=email
#                           , is_active = True
#                           , last_login = timezone.now()
#                           , **extra_fields )
#         user.set_password(password)
#         user.save(using=self._db)

#     def create_user(self,username,password=None, email=None, **extra_fields):
#         return self._create_user(username, password, email, **extra_fields)
    

# class Usuario(AbstractBaseUser,PermissionsMixin):
#     email = models.EmailField(_('dirección email'), max_length=254, unique=True)
#     first_name = models.CharField(_('nombres'), max_length=30, blank=True)
#     last_name = models.CharField(_("apellidos"), max_length=30, blank=True)
#     is_staff = models.BooleanField(_('administrador?'), default=False,
#                                    help_text='Usuario puede iniciar sesión en admin')
#     is_active = models.BooleanField(_('activo'),default=True,
#                                     help_text=_("Si el usuario está desactivado no podrá acceder a la plataforma"))
#     date_joined = models.DateTimeField(_('fecha de registro'), default=timezone.now)

#     objects = UsuarioManager

#     class Meta:
#         verbose_name=_("usuario")
#         verbose_name_plural = _("usuarios")

#     def get_absolte_url(self):
#         return "/users/%s" % urlquote(self.email)
    
#     def get_full_name(self):
#         fn = "%s %s" % (self.first_name, self.last_name)
#         return fn.strip()
    
#     def get_short_name(self):
#         return self.first_name