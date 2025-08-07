from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin\
    , PermissionRequiredMixin
from django.db import connection
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password

from solicitudes.models import Asignacion
from operaciones.models import Documentos, Asignacion as Operaciones, Pagares
from cobranzas.models import Cheques_protestados
from contabilidad.models import Factura_venta

from datetime import date, timedelta
from .models import Usuario_empresa, Version_detalle, Versiones
from .forms import Userform, UserPasswordForm

class Home(LoginRequiredMixin, generic.ListView):
    template_name='bases/home.html'
    login_url='bases:login'
    model = Version_detalle
    context_object_name='detalle_version'

    def get_queryset(self) :
        qs=Version_detalle.objects.filter( version__lultimaversion = True,)
        return qs
    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        version = Versiones.objects.filter( lultimaversion = True,).first()
        context["version"]=version

        return context

class MixinFormInvalid:
    def form_invalid(self,form):
        response = super().form_invalid(form)
        if response.status_code != 200:
            if self.request.is_ajax():
                return JsonResponse(form.errors, status=400)
            # else:
        return response

class SinPrivilegios(LoginRequiredMixin, PermissionRequiredMixin, MixinFormInvalid):
    login_url = 'bases:login'
    raise_exception=False
    redirect_field_name="redirecto_to"

    def handle_no_permission(self):
        from django.contrib.auth.models import AnonymousUser
        if not self.request.user==AnonymousUser():
            self.login_url='bases:sin_permisos'
        return HttpResponseRedirect(reverse_lazy(self.login_url))

class HomeSinPrivilegios(LoginRequiredMixin, generic.TemplateView):
    login_url = "bases:login"
    template_name="bases/sin_privilegios.html"

def enviarPost(procedimiento):
    # se ejecuta en vistas que llaman a stored procedures con parametros OUT.
    # El fetchone regresará una arreglo de los parámetros de salida del tipo:
    # ('OK',123456) según la cantidad y tipo de parámetros OUT, donde siempre
    # el primer elemento es el resultado del parametro StrError , que si no 
    # hay errores devolverá la expresión 'OK'.
    try:
                
        with connection.cursor()   as cursor:
            cursor.execute(procedimiento)
            resultado=cursor.fetchone()
    except Exception as error:
            resultado="Error:"+str(error)
    finally:
        cursor.close()
    return resultado

def enviarConsulta(consulta):
    # se ejecuta en vistas que llaman a stored procedures .
    # fetchall recibe todos los datos y son obtenidos como tipo json
    try:
                
        with connection.cursor()   as cursor:
            cursor.execute(consulta)
            resultado=cursor.fetchall()
    except Exception as error:
            resultado="Error:"+str(error)
    finally:
        cursor.close()
    return resultado

def numero_a_letras(numero):
    indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
    entero = int(numero)
    decimal = int(round((numero - entero)*100))
	#print 'decimal : ',decimal 
    contador = 0
    numero_letras = ""
    while entero >0:
        a = entero % 1000
        if contador == 0:
            en_letras = convierte_cifra(a,1).strip()
        else :
            en_letras = convierte_cifra(a,0).strip()
        if a==0:
            numero_letras = en_letras+" "+numero_letras
        elif a==1:
            if contador in (1,3):
                numero_letras = indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
        else:
            numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
        numero_letras = numero_letras.strip()
        contador = contador + 1
        entero = int(entero / 1000)
    numero_letras = numero_letras+" con " + str(decimal) +"/100"
	# print 'numero: ',numero
	# print numero_letras
    return numero_letras
 
def convierte_cifra(numero,sw):
    lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
    lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
        ("VEINTE","VEINTI"),("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
        ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
        ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
        ("NOVENTA" , "NOVENTA Y ")
        ]
    lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
    centena = int (numero / 100)
    decena = int((numero -(centena * 100))/10)
    unidad = int(numero - (centena * 100 + decena * 10))
	#print "centena: ",centena, "decena: ",decena,'unidad: ',unidad
 
    texto_centena = ""
    texto_decena = ""
    texto_unidad = ""
 
	#Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad)!=0:
            texto_centena = texto_centena[1]
        else :
            texto_centena = texto_centena[0]
 
	#Valida las decenas
    texto_decena = lista_decena[decena]
    if decena == 1 :
        texto_decena = texto_decena[unidad]
    elif decena > 1 :
        if unidad != 0 :
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]
 	#Validar las unidades
 	#print "texto_unidad: ",texto_unidad
    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw]
 
    return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)

@login_required(login_url='/login/')
@permission_required('operaciones.view_documentos', login_url='bases:sin_permisos')
def dashboard(request):
    template_name='bases/dashboard.html'
    # para que tome todo el día de hoy estoy poniendo hasta mañana
    desde = date.today() + timedelta(days=-1)
    hasta = date.today() + timedelta(days=1)
    cartera = 0
    protestos = 0
    pagares = 0

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    docs = Documentos.objects.TotalCartera(id_empresa.empresa)
    if docs['Total']:
        cartera = docs['Total']
        
    prot = Cheques_protestados.objects.TotalProtestos(id_empresa.empresa)
    if prot['Total']:
        protestos = prot['Total']

    pag = Pagares.objects.TotalPagares(id_empresa.empresa)
    if pag['Total']:
        pagares = pag['Total']

    sp = Asignacion.objects\
        .pendientes_o_rechazadas(empresa = id_empresa.empresa).count()

    # obtener el último año de proceso
    ultimo_registro = Operaciones.objects.order_by('-dregistro').first()
    total_negociado = Operaciones.objects.total_negociado(id_empresa.empresa)
    ingresos_año = Factura_venta.objects.ingresos_delaño(id_empresa.empresa
                                                        ,ultimo_registro.dnegociacion.year)

    datos = { 'desde':desde
        , 'hasta':hasta
        , 'total_cartera': cartera
        , 'total_protestos':protestos
        , 'total_cartera_protestos':cartera+protestos+pagares
        , 'solicitudes_pendientes':sp
        , 'año':ultimo_registro.dnegociacion.year
        , 'total_negociado': total_negociado['Total']
        , 'ingreso_acumulado': ingresos_año['Total']
    }
    return render(request, template_name, datos)

@login_required(login_url='/login/')
# @permission_required('???.change_user', login_url='bases:sin_permisos')
def user_editar(request,pk=None):
    template_name = "bases/editar_usuario.html"
    context = {}
    form = None
    obj = None

    if request.method == "GET":
        if not pk:
            form = Userform(instance = None )
        else:
            obj = User.objects.filter(id=pk).first()
            form = Userform(instance = obj)
        context["form"] = form
        context["obj"] = obj

        # grupos_usuarios = None
        # grupos = None
        # if obj:
        #     grupos_usuarios = obj.groups.all()
        #     grupos = Group.objects.filter(~Q(id__in=obj.groups.values('id')))
        
        # context["grupos_usuario"]=grupos_usuarios
        # context["grupos"]=grupos
    
    if request.method == "POST":
        data = request.POST
        e = data.get("email")
        fn = data.get("first_name")
        ln = data.get("last_name")

        if pk:
            obj = User.objects.filter(id=pk).first()
            if not obj:
                print("Error Usuario No Existe")
            else:
                obj.email = e
                obj.first_name = fn
                obj.last_name = ln
                obj.save()
        else:
            obj = User.objects.create_user(
                email = e,
                first_name = fn,
                last_name = ln
            )
        return redirect('bases:home')
    
    return render(request,template_name,context)

@login_required(login_url='/login/')
# @permission_required('???.change_user', login_url='bases:sin_permisos')
def user_password(request,pk):
    template_name = "bases/password_usuario.html"
    context = {}

    obj = User.objects.filter(id=pk).first()
    form = UserPasswordForm(instance = obj)

    context["obj"] = obj
    context["form"] = form

    if not obj:
        print("Error Usuario No Existe")

    # if request.method == "GET":
    
    if request.method == "POST":
        data = request.POST
        p = data.get("password")
        p2 = data.get("password2")
        if p != p2:
            context["error"] = 'No existe coincidencia con la confirmación. '
        else:
            obj.password = make_password(p)
            obj.save()
            return redirect('bases:home')
    
    return render(request,template_name,context)


