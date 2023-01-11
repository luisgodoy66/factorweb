from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin\
    , PermissionRequiredMixin
from django.db import connection
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy

from solicitudes.models import Asignacion
from datetime import date, timedelta

class Home(LoginRequiredMixin, generic.TemplateView):
    # model = Asignacion
    template_name='bases/home.html'
    login_url='bases:login'
    # context_object_name='consulta'

class MixinFormInvalid:
    def form_invalid(self,form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

class SinPrivilegios(LoginRequiredMixin, PermissionRequiredMixin, MixinFormInvalid):
    login_url = 'bases:login'
    raise_exception=False
    redirect_field_name="redirecto_to"

    def handle_no_permission(self):
        from django.contrib.auth.models import AnonymousUser
        if not self.request.user==AnonymousUser():
            self.login_url='bases:sin_privilegios'
        return HttpResponseRedirect(reverse_lazy(self.login_url))

class HomeSinPrivilegios(LoginRequiredMixin, generic.TemplateView):
    login_url = "bases:login"
    template_name="bases/sin_privilegios.html"

def SolicitudesPendientes(request):
    template_name='bases/home.html'

    sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
    datos = {
        'asignaciones_pendientes':sp
    }
    return render(request, template_name, datos)

def enviarPost(consulta):
    # se ejecuta en vistas que llaman a stored procedures con parametros OUT.
    # El fetchone regresará una arreglo de los parámetros de salida del tipo:
    # ('OK',123456) según la cantidad y tipo de parámetros OUT, donde siempre
    # el primer elemento es el resultado del parametro StrError , que si no 
    # hay errores devolverá la expresión 'OK'.
    try:
                
        with connection.cursor()   as cursor:
            cursor.execute(consulta)
            resultado=cursor.fetchone()
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

def dashboard(request):
    template_name='bases/dashboard.html'
    # para que tome todo el día de hoy estoy poniendo hasta mañana
    desde = date.today() + timedelta(days=-1)
    hasta = date.today() + timedelta(days=1)

    datos = { 'desde':desde
        , 'hasta':hasta
    }
    return render(request, template_name, datos)
