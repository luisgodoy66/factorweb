from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.urls import reverse_lazy

from .models import Documentos_cabecera, Documentos_detalle, Liquidacion_cabecera\
    , Cheques_protestados, Cheques, Recuperaciones_cabecera\
    , Documentos_protestados, Recuperaciones_detalle
from operaciones.models import Documentos, ChequesAccesorios, Datos_operativos\
    , Desembolsos, Motivos_protesto_maestro, Cargos_detalle, Notas_debito_cabecera\
    , Notas_debito_detalle
from clientes.models import Cuentas_bancarias, Datos_generales, Cuenta_transferencia
from empresa.models import Tasas_factoring, Cuentas_bancarias as CuentasEmpresa\
    , Datos_participantes

from .forms import CobranzasDocumentosForm, ChequesForm, LiquidarForm\
    , MotivoProtestoForm, ProtestoForm, RecuperacionesProtestosForm

from operaciones.forms import DesembolsarForm

from datetime import date, timedelta
from decimal import Decimal

import json
import math

from bases.views import enviarPost, numero_a_letras

class DocumentosVencidosView(LoginRequiredMixin, generic.ListView):
    model = Documentos
    template_name = "cobranzas/listadocumentospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_context_data(self,*args, **kwargs): 
        context = super(DocumentosVencidosView, self).get_context_data(*args,**kwargs) 
        fecha_corte = date.today() 
        context['fecha_corte'] =  fecha_corte
        context['filtro'] = 'No'

        return context

class DocumentosPorVencerView(LoginRequiredMixin, generic.ListView):
    model = Documentos
    template_name = "cobranzas/listadocumentospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_context_data(self,*args, **kwargs): 
        context = super(DocumentosPorVencerView, self).get_context_data(*args,**kwargs) 
        fecha_corte = date.today() + timedelta(days=7)
        context['fecha_corte'] =  fecha_corte
        context['filtro'] = 'Si'

        return context

class ChequesADepositarView(LoginRequiredMixin, generic.ListView):
    # la lista se obtiene desde url en la tabla bt, 
    # el model indicado es solo para fluir con el django. No se usa.
    model = ChequesAccesorios
    template_name = "cobranzas/listachequesadepositar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_context_data(self,*args, **kwargs): 
        context = super(ChequesADepositarView, self).get_context_data(*args,**kwargs) 
        fecha_corte = date.today() 
        context['fecha_corte'] =  fecha_corte#.strftime("%Y-%m-%d")

        return context

class CobranzasDocumentosView(LoginRequiredMixin, generic.FormView):
    model = Documentos_cabecera
    template_name = "cobranzas/datoscobranzas_form.html"
    context_object_name='cobranza'
    login_url = 'bases:login'
    form_class = CobranzasDocumentosForm

    # recibe como parametros los id's de los documentos a cobrar
    # los pasa al html para que se pasen al js que carga el detalle
    def get_context_data(self, **kwargs):

        docs = self.kwargs.get('ids_documentos')
        total_cartera=self.kwargs.get('total_cartera')
        forma_cobro=self.kwargs.get('forma_cobro')
        cliente_ruc = self.kwargs.get('cliente_ruc')
        un_solo_deudor = self.kwargs.get('un_comprador')
        deudor_id = self.kwargs.get('deudor_id')
        tipo_factoring = self.kwargs.get('tipo_factoring')

        cliente = Datos_generales.objects.filter(cxcliente = cliente_ruc).first()

        cuentas = Cuentas_bancarias\
            .objects.filter(cxparticipante = cliente_ruc \
                , leliminado = False, lpropia = True).all()
                # , cxtipocuenta = 'C').all()
        
        cuentas_deudor = None

        if un_solo_deudor=="Si":
            cuentas_deudor = Cuentas_bancarias\
                .objects.filter(cxparticipante = deudor_id \
                    , leliminado = False, lpropia = True).all()
                    # , cxtipocuenta = 'C').all()   # podr??a hacer transferencias desde cuenta de ahorros

        # Call the base implementation first to get a context
        context = super(CobranzasDocumentosView, self).get_context_data(**kwargs)
        context["documentos"] = docs
        context["total_cartera"] = total_cartera
        context["forma_cobro"] = forma_cobro
        context["form_cheque"] = ChequesForm
        context["cuentas_bancarias_cliente"] = cuentas
        context["cuentas_bancarias_deudor"] = cuentas_deudor
        context["un_solo_comprador"] = un_solo_deudor
        context["cliente_id"] = cliente_ruc
        context["cliente"] = cliente
        context["tipo_factoring"] = tipo_factoring
        context["deudor_id"] = deudor_id

        return context
from django.db.models.expressions import RawSQL 

class CobranzasConsulta(LoginRequiredMixin, generic.ListView):
    model = Documentos_cabecera
    template_name = "cobranzas/consultageneralcobranzas.html"
    context_object_name='consulta'
    login_url = 'bases:login'
 

class CobranzasPorConfirmarView(LoginRequiredMixin, generic.ListView):
    # la lista se obtiene desde url en la tabla bt, 
    # el model indicado es solo para fluir con el django. No se usa.
    model = Documentos_cabecera
    template_name = "cobranzas/listacobranzasporconfirmar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        cobranzas = Documentos_cabecera.objects.filter(cxestado='A'\
            , leliminado = False\
            , cxformapago__in = ['TRA','CHE','DEP']\
            , cxtipofactoring__lanticipatotalnegociado = False )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion'
                ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'C'",''))
                
        recuperaciones = Recuperaciones_cabecera.objects.filter(cxestado='A'\
            , leliminado = False\
            , cxformacobro__in = ['TRA','CHE']\
            , cxtipofactoring__lanticipatotalnegociado = False )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion'
                ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'R'",''))

        return cobranzas.union(recuperaciones)

class CobranzasPendientesLiquidarView(LoginRequiredMixin, generic.ListView):
    model = Documentos_cabecera
    template_name = "cobranzas/listacobranzaspendientesliquidar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        cobranzas= Documentos_cabecera.objects.filter(Q(cxestado='C',\
            leliminado = False) | Q(cxformapago__in=["EFE", "MOV"], cxestado='A'))\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion'
                ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'C'",''))

        recuperaciones = Recuperaciones_cabecera.objects.filter(Q(cxestado='C',\
            leliminado = False) | Q(cxformacobro__in=["EFE", "MOV"], cxestado='A'))\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion'
                ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'R'",''))

        return cobranzas.union(recuperaciones)

# class CobranzaPorCondonarView(LoginRequiredMixin, generic.FormView):
#     model = Documentos_cabecera
#     template_name = "cobranzas/detallecobroporcondonar.html"
#     context_object_name='cobranza'
#     login_url = 'bases:login'
#     form_class = CobranzasDocumentosForm

#     def get_context_data(self, **kwargs):

#         tipo = self.kwargs.get('tipo_operacion')

#         # Call the base implementation first to get a context
#         context = super(CobranzasDocumentosView, self).get_context_data(**kwargs)
#         context["tipo_operacion"] = tipo

#         return context

def CobranzaPorCondonar(request,pk, tipo_operacion):
    template_name = "cobranzas/detallecobroporcondonar.html"
    formulario={}
    
    if tipo_operacion=='C':
        operacion = Documentos_cabecera.objects.filter(pk=pk).first()
        formulario = CobranzasDocumentosForm
    else:
        operacion = Recuperaciones_cabecera.objects.filter(pk=pk).first()
        formulario = RecuperacionesProtestosForm

    contexto={"operacion": operacion
        , "form" : formulario
        , "tipo_operacion": tipo_operacion
        }
    
    return render(request, template_name, contexto)


class LiquidacionesPendientesPagarView(LoginRequiredMixin, generic.ListView):
    model = Liquidacion_cabecera
    template_name = "cobranzas/listaliquidacionespendientespagar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        return Liquidacion_cabecera.objects.filter(ldesembolsada=False,\
            leliminado = False, ddesembolso__lte = date.today())

class MotivosProtestoView(LoginRequiredMixin, generic.ListView):
    model = Motivos_protesto_maestro
    template_name = "cobranzas/listamotivosprotesto.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class MotivoProtestoNew(LoginRequiredMixin, generic.CreateView):
    model = Motivos_protesto_maestro
    template_name = "cobranzas/datosmotivoprotesto_form.html"
    form_class = MotivoProtestoForm
    context_object_name='motivo'
    success_url= reverse_lazy("cobranzas:listamotivosprotesto")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class MotivoProtestoEdit(LoginRequiredMixin, generic.UpdateView):
    model = Motivos_protesto_maestro
    template_name = "cobranzas/datosmotivoprotesto_form.html"
    context_object_name='motivo'
    login_url = 'bases:login'
    form_class = MotivoProtestoForm
    success_url= reverse_lazy("cobranzas:listamotivosprotesto")

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class ProtestoCobranzaNew(LoginRequiredMixin, generic.CreateView):
    model=Cheques_protestados
    template_name="cobranzas/datosprotesto_form.html"
    context_object_name = "consulta"
    form_class=ProtestoForm
    success_url=reverse_lazy("cobranzas:listacobranzasporconfirmar")
    success_message="Protesto creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_cheque = self.kwargs.get('id_cheque')
        id_cobranza = self.kwargs.get('id_cobranza')

        cheque = Cheques.objects.filter(pk=id_cheque).first()
        cobranza = Documentos_cabecera.objects.filter(pk = id_cobranza).first()

        # Call the base implementation first to get a context
        context = super(ProtestoCobranzaNew, self).get_context_data(**kwargs)
        context["cheque"]=cheque
        context["cobranza"] = cobranza
        context["id_cliente"] = cobranza.cxcliente.cxcliente.cxparticipante
        context["forma_cobro"] = cobranza.cxformapago
        context["codigo_cobranza"] = cobranza.cxcobranza
        context["tipo_operacion"]='Cobranza'

        return context

class ProtestosPendientesView(LoginRequiredMixin, generic.ListView):
    model = Cheques_protestados
    template_name = "cobranzas/listaprotestospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class RecuperacionProtestoView(LoginRequiredMixin, generic.FormView):
    model = Recuperaciones_cabecera
    template_name = "cobranzas/datosrecuperacion_form.html"
    context_object_name='cobranza'
    login_url = 'bases:login'
    form_class = RecuperacionesProtestosForm

    # recibe como parametros los id's de los protestos a cobrar
    # los pasa al html para que se pasen al js que carga el detalle
    def get_context_data(self, **kwargs):

        protestos = self.kwargs.get('ids_protestos')
        total_cartera=self.kwargs.get('total_cartera')
        forma_cobro=self.kwargs.get('forma_cobro')
        participante_id = self.kwargs.get('cliente_ruc')
        tipo_factoring = self.kwargs.get('tipo_factoring')
        # nota: debe tomar del tipo de factoring el con o sin recurso
        modalidad_factoring='CR'

        cliente = Datos_participantes.objects\
            .filter(cxparticipante = participante_id).first()

        cuentas = Cuentas_bancarias\
            .objects.filter(cxparticipante = participante_id \
                , leliminado = False, lpropia = True).all()
                # , cxtipocuenta = 'C').all()
        

        # Call the base implementation first to get a context
        context = super(RecuperacionProtestoView, self).get_context_data(**kwargs)
        context["protestos"] = protestos
        context["total_cartera"] = total_cartera
        context["forma_cobro"] = forma_cobro
        context["form_cheque"] = ChequesForm
        context["cuentas_bancarias_participante"] = cuentas
        context["cliente_id"] = participante_id
        context["cliente"] = cliente
        context["tipo_factoring"] = tipo_factoring
        context["modalidad_factoring"]=modalidad_factoring

        return context

class ProtestoRecuperacionNew(LoginRequiredMixin, generic.CreateView):
    model=Cheques_protestados
    template_name="cobranzas/datosprotesto_form.html"
    context_object_name = "consulta"
    form_class=ProtestoForm
    success_url=reverse_lazy("cobranzas:listacobranzasporconfirmar")
    success_message="Protesto creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_cheque = self.kwargs.get('id_cheque')
        id_cobranza = self.kwargs.get('id_cobranza')

        cheque = Cheques.objects.filter(pk=id_cheque).first()
        cobranza = Recuperaciones_cabecera.objects.filter(pk = id_cobranza).first()

        # Call the base implementation first to get a context
        context = super(ProtestoRecuperacionNew, self).get_context_data(**kwargs)
        context["cheque"]=cheque
        context["cobranza"] = cobranza
        context["id_cliente"] = cobranza.cxcliente.cxcliente.cxparticipante
        context["forma_cobro"] = cobranza.cxformacobro
        context["codigo_cobranza"] = cobranza.cxrecuperacion
        context["tipo_operacion"]='Recuperacion'

        return context

def GeneraListaCarteraPorVencerJSON(request, fecha_corte = None):
    # Es invocado desde la url de una tabla bt
    # if not fecha_corte: 
    #     fecha = date.today()
    #     fecha = fecha + timedelta(days=7)

    documentos = Documentos.objects.cartera_pendiente(fecha_corte).all()

    tempBlogs = []
    for i in range(len(documentos)):
        tempBlogs.append(GeneraListaCarterPorVencerJSONSalida(documentos[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaCarterPorVencerJSONSalida(doc):
    output = {}

    output['id'] = doc.id
    output["IdCliente"] = doc.cxcliente.cxparticipante
    output["Cliente"] = doc.cxcliente.ctnombre
    output["IdComprador"] = doc.cxcomprador.cxparticipante
    output["Comprador"] = doc.cxcomprador.ctnombre
    output["IdTipoFactoring"] = doc.cxtipofactoring.cxtipofactoring
    output["TipoFactoring"] = doc.cxtipofactoring.ctabreviacion
    output["Asignacion"] = doc.cxasignacion.cxasignacion
    output["Documento"] = doc.ctdocumento
    output["Vencimiento"] = doc.dvencimiento.strftime("%Y-%m-%d")
    output["Saldo"] = doc.nsaldo
    if doc.dultimacobranza:
        output["UltimaCobranza"] = doc.dultimacobranza.strftime("%Y-%m-%d")
    else:
        output["UltimaCobranza"] =''

    return output

def DetalleDocumentosFacturasPuras(request, ids_documentos):
    # filtrar los documentos correspondientes a la lista pasada
    documentos = Documentos.objects\
        .filter(id__in = ids_documentos.split(','), leliminado = False)
    
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(documentos)):
        tempBlogs.append(DocumentoADictionario(documentos[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DocumentoADictionario(doc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    # los datos aqu?? van a obtenerse con el getData de la tb, aunque no se 
    # presenten en el HTML
    output = {}
    output['id'] = doc.id
    output["IdComprador"] = doc.cxcomprador.cxparticipante
    output["Comprador"] = doc.cxcomprador.ctnombre
    output["Asignacion"] = doc.cxasignacion.cxasignacion
    output["Documento"] = doc.ctdocumento
    output["PorcentajeAnticipo"] = doc.nporcentajeanticipo
    output["Emision"] = doc.demision.strftime("%Y-%m-%d")
    output["Vencimiento"] = doc.dvencimiento.strftime("%Y-%m-%d")
    output["SaldoActual"] = doc.nsaldo
    output["Cobro"] = doc.nsaldo
    output["Retenido"] = "0.0"
    output["Bajas"] = "0.00"
    output["SaldoFinal"] = "0.0"

    return output

def DatosCobro(request, id, asgn, doc, sdo, cobro, retenido, baja):
    template_name = "cobranzas/datoscobro_modal.html"
    contexto={
        "id": id,
        "asignacion" : asgn,
        "documento" : doc,
        "saldo" : sdo,
        "valor_cobrado": cobro,
        "valor_retenido":retenido,
        "baja":baja,
    }
    return render(request, template_name, contexto)

def AceptarCobranza(request):
    # ejecuta un store procedure 
    # Devuelve el control a un proceso js
    resultado = 'OK'
    nc=' '; gi=' '; es_cc = False; cd = 0; fd = 'Null'

    objeto=json.loads(request.body.decode("utf-8"))

    id_cliente=objeto["id_cliente"]
    tipo_factoring=objeto["tipo_factoring"]
    forma_cobro=objeto["forma_cobro"]
    fecha_cobro=objeto["fecha_cobro"]
    valor_recibido=objeto["valor_recibido"]
    pagador_por_cliente=objeto["pagador_por_cliente"]
    sobrepago=objeto["sobrepago"]
    cuenta_bancaria = objeto["cuenta_bancaria"]
    nusuario = request.user.id
    id_deudor=objeto["id_deudor"]
    # los siguientes son maps:
    # si debo procesar aqui uso json.loads para trabajar como diccionarios
    # si quiero enviar como parametro al store procedure paso tal cual y se recibe
    # como objeto json
    cheque = json.loads(objeto["arr_cheque"])         
    deposito=json.loads(objeto["arr_deposito"]) 
    documentos_cobrados=objeto["arr_documentos_cobrados"]

    if cheque:
        nc = cheque["numero_cheque"]
        gi = cheque["girador"]
    
    if deposito:
        es_cc = deposito["deposito_cuenta_conjunta"]
        cd = deposito["cuenta_deposito"]
        fd = "'"  + deposito["fecha_deposito"] + "'"

        if not cd :
            if es_cc :
                cd = 'Null'
            else:
                return HttpResponse("Debe especificar la cuenta de dep??sito")

    if not cuenta_bancaria:
        cuenta_bancaria='Null'
    
    # Los 2 ultimos parametros son el id de cheque accesorio y el mensaje de error
    resultado=enviarPost("CALL uspAceptarCobranzaCartera( '{0}','{1}','{2}','{3}',{4}\
        ,{5},{6},{7}\
        ,'{8}','{9}',{10},{11},{12}\
        ,'{13}', '{14}',{15},Null,'',0)"
        .format(id_cliente, tipo_factoring, forma_cobro, fecha_cobro, valor_recibido
        ,pagador_por_cliente,sobrepago,cuenta_bancaria
        ,nc,gi,es_cc, cd, fd
        ,documentos_cobrados, id_deudor,nusuario))

    return HttpResponse(resultado)

def GeneraListaChequesADepositarJSON(request, fecha_corte):
    # Es invocado desde la url de una tabla bt

    documentos = ChequesAccesorios.objects.cheques_a_depositar(fecha_corte).all()

    tempBlogs = []
    for i in range(len(documentos)):
        tempBlogs.append(GeneraListaChequesADepositarJSONSalida(documentos[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    return HttpResponse(JsonResponse( data))

def GeneraListaChequesADepositarJSONSalida(doc):
    output = {}

    output['id'] = doc.id
    output["IdCliente"] = doc.documento.cxcliente.cxparticipante
    output["Cliente"] = doc.documento.cxcliente.ctnombre
    output["IdComprador"] = doc.documento.cxcomprador.cxparticipante
    output["Comprador"] = doc.documento.cxcomprador.ctnombre
    output["IdTipoFactoring"] = doc.documento.cxtipofactoring.cxtipofactoring
    output["TipoFactoring"] = doc.documento.cxtipofactoring.ctabreviacion
    output["Asignacion"] = doc.documento.cxasignacion.cxasignacion
    output["Documento"] = doc.documento.ctdocumento
    output["Vencimiento"] = doc.dvencimiento.strftime("%Y-%m-%d")
    output["Valor"] = doc.ntotal
    output["Datos"] = doc.cxbanco.ctbanco +' CTA.'+ doc.ctcuenta + ' CH/' + doc.ctcheque

    return output

from django.db.models import Count, Sum

def DepositoCheques(request, ids_cheques, total_cartera):
    template_name = "cobranzas/depositocheques_form.html"
    contexto={}
    result={}

    if request.method =='GET':

        result = (ChequesAccesorios.objects.filter(id__in = ids_cheques.split(','))
            .values( 'documento__cxcliente__ctnombre')
            .annotate(pcount=Count('documento'))
            .annotate(total = Sum('ntotal'))
            .order_by()
        )        
    # Call the base implementation first to get a context
    contexto = {"cheques" : result
        ,"total_cartera" : total_cartera
        ,"form": CobranzasDocumentosForm
        }

    if request.method == 'POST':

        cd=request.POST.get("cxcuentadeposito")
        fd=request.POST.get("ddeposito")

        resultado=enviarPost("CALL uspDepositarChequesAccesorios( '{0}',{1},'{2}'\
            ,{3},'')"
            .format(ids_cheques,cd, fd, request.user.id))

        if resultado[0] !='OK':
            return HttpResponse(resultado)

        return redirect("cobranzas:listachequesadepositar")


    return render(request, template_name, contexto)

def GeneraListaCobranzasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    if desde == 'None':
        cobranzas = Documentos_cabecera.objects.all()\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                ,'cxcheque', 'cxestado', 'dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
        recuperaciones = Recuperaciones_cabecera.objects.all()\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro'
                ,'nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))
        protestos_cobranzas = Documentos_cabecera.objects\
            .filter(cxestado='P')\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C protestada'",''))
        protestos_recuperaciones = Recuperaciones_cabecera.objects\
            .filter(cxestado='P')\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R protestada'",''))
    else:

        cobranzas = Documentos_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
                
        recuperaciones = Recuperaciones_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))

        protestos_cobranzas = Documentos_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta, cxestado='P')\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C protestada'",''))
                    
        protestos_recuperaciones = Recuperaciones_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta, cxestado='P')\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R protestada'",''))

        # Documentos_cabecera.objects.filter(cxestado='P').values('cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto')                

    movimiento = cobranzas.union(recuperaciones, protestos_cobranzas, protestos_recuperaciones)
            
    tempBlogs = []
    for i in range(len(movimiento)):
        tempBlogs.append(GeneraListaCobranzasJSONSalida(movimiento[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaCobranzasJSONSalida(transaccion):
    output = {}
    output['id'] = transaccion['id']
    output["Cliente"] = transaccion['cxcliente__cxcliente__ctnombre']
    output["Operacion"] = transaccion['cxcobranza']
    output["Fecha"] = transaccion['dcobranza'].strftime("%Y-%m-%d")
    output["Estado"] = transaccion['cxestado']
    output["Valor"] =  transaccion['nvalor']
    output["TipoFactoring"] = transaccion['cxtipofactoring__ctabreviacion']
    output["Registro"] = transaccion["dregistro"]

    if 'protestada' in transaccion['tipo']:
        output["Detalle"] = transaccion['cxformapago']
    else:
        if transaccion['cxformapago'] =="CHE" or transaccion['cxformapago'] =="DEP":
            cheque = Cheques.objects.filter(pk = transaccion['cxcheque']).first()
            output["Detalle"] = cheque.__str__()
        elif transaccion['cxformapago'] =="TRA":
            cuenta = Cuentas_bancarias.objects\
                .filter(pk = transaccion['cxcuentatransferencia']).first()
            output["Detalle"] = cuenta.__str__()

        if transaccion['ddeposito']:
            output["Deposito"] = transaccion['ddeposito'].strftime("%Y-%m-%d")
        output["FormaCobro"] = transaccion['cxformapago']
        output["Sobrepago"] = transaccion['nsobrepago']

    if transaccion['tipo'] =='C':
        output["Movimiento"] = 'Cobranza'
    elif transaccion['tipo'] =='R':
        output["Movimiento"] = 'Recuperaci??n'
    elif transaccion['tipo'] =='C protestada':
        output["Movimiento"] = 'Cobranza protestada'
    elif transaccion['tipo'] =='R protestada':
        output["Movimiento"] = 'Recuperaci??n protestada'

    # se necesita el tipo de operacion para saber que va a imprimir o reversar
    output["TipoOperacion"] = transaccion["tipo"]
    output["FormaPago"] = transaccion["cxformapago"]

    return output

@login_required(login_url='/login/')
@permission_required('cobranzas.update_documentos_cabecera', login_url='bases:sin_permisos')
def ConfirmarCobranza(request, cobranza_id, tipo_operacion):
    # la eliminacion es l??gica
    # debe devolver: 1 si esta bien, 0 si esta mal

    if tipo_operacion=='C':
        cobr = Documentos_cabecera.objects.filter(pk=cobranza_id).first()
    else:
        cobr = Recuperaciones_cabecera.objects.filter(pk=cobranza_id).first()

    if not cobr:
        return HttpResponse("Cobranza no encontrada")

    if request.method=="GET":
        # cobr.cxusuarioatencion = request.user.id
        cobr.cxestado = "C"
        cobr.save()

    return HttpResponse("OK")

def DetalleDocumentosCobrados(request, cobranza_id, tipo_operacion):
    # filtrar los documentos correspondientes a la lista pasada

    if tipo_operacion=='C':
        detalle = Documentos_detalle.objects\
            .filter(cxcobranza = cobranza_id, leliminado = False)
    else:
        detalle = Recuperaciones_detalle.objects\
            .filter(recuperacion = cobranza_id, leliminado = False)
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(detalle)):
        if tipo_operacion=='C':
            tempBlogs.append(DetalleDocumentosCobradosSalida(detalle[i])) # Converting `QuerySet` to a Python Dictionary
        else:
            tempBlogs.append(DetalleDocumentosRecuperadosSalida(detalle[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": detalle.count(),
        "totalNotFiltered": detalle.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DetalleDocumentosCobradosSalida(doc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    output = {}
    output['id'] = doc.id
    output["Comprador"] = doc.cxdocumento.cxcomprador.ctnombre
    output["Asignacion"] = doc.cxdocumento.cxasignacion.cxasignacion
    output["Documento"] = doc.cxdocumento.ctdocumento
    output["Vencimiento"] = doc.vencimiento().strftime("%Y-%m-%d")
    output["DiasVencidos"] = doc.dias_vencidos()
    output["DiasCondonados"] = doc.ndiasacondonar
    if doc.cxusuariocondona:
        output["UsuarioCondona"] = doc.cxusuariocondona.username
    output["Valor"] = doc.nvalorcobranza
    return output

def DetalleDocumentosRecuperadosSalida(doc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    output = {}
    output['id'] = doc.id
    output["Comprador"] = doc.documentoprotestado.documento.cxcomprador.ctnombre
    output["Asignacion"] = doc.documentoprotestado.documento.cxasignacion.cxasignacion
    output["Documento"] = doc.documentoprotestado.documento.ctdocumento
    output["Vencimiento"] = doc.vencimiento().strftime("%Y-%m-%d")
    output["DiasVencidos"] = doc.dias_vencidos()
    output["DiasCondonados"] = doc.ndiasacondonar
    if doc.cxusuariocondona:
        output["UsuarioCondona"] = doc.cxusuariocondona.username
    output["Valor"] = doc.nvalorrecuperacion

    return output

def DatosDiasACondonar(request, id, dias, cobranza_id, tipo_operacion):
    template_name = "cobranzas/datosdiasacondonar_modal.html"
    contexto={
        "id": id,
        "dias":dias,
        "cobranza": cobranza_id,
        "tipo_operacion": tipo_operacion
    }
    if request.method =="POST":
        dias = request.POST.get("dias_id")
        
        if tipo_operacion =='C':
            cobro = Documentos_detalle.objects.filter(pk=id).first()
        else:
            cobro = Recuperaciones_detalle.objects.filter(pk=id).first()

        if cobro:
            cobro.ndiasacondonar = dias
            cobro.cxusuariocondona = request.user
            cobro.save()
        else:
            return "cobranza/recuperaci??n no encontrada"

        return redirect("cobranzas:cobranzaporcondonar", pk=cobranza_id, tipo_operacion=tipo_operacion)
        
        
    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('cobranzas.update_documentos_cabecera', login_url='bases:sin_permisos')
def ReversaConfirmacionCobranza(request, cobranza_id, tipo_operacion):
    # la eliminacion es l??gica
    # debe devolver: 1 si esta bien, 0 si esta mal

    if tipo_operacion =='C':
        cobr = Documentos_cabecera.objects.filter(pk=cobranza_id).first()
    else:
        cobr = Recuperaciones_cabecera.objects.filter(pk=cobranza_id).first()

    if not cobr:
        return HttpResponse("Cobranza no encontrada")

    if request.method=="GET":
        # cobr.cxusuarioatencion = request.user.id
        cobr.cxestado = "A"
        cobr.save()

    return HttpResponse("OK")

from django.db.models import Q

def GeneraListaCobranzasPendientesProcesarJSON(request):
    # Es invocado desde la url de una tabla bt
    # son liquidables las que est??n confirmadas ademas de los cobros en efectivo y
    # movimientos contables
    # movimiento = Documentos_cabecera.objects.filter(Q(cxestado='C',\
    #         leliminado = False) | Q(cxformapago__in=["EFE", "MOV"], cxestado='A'))
    cobranzas= Documentos_cabecera.objects.filter(Q(cxestado='C',\
        leliminado = False) | Q(cxformapago__in=["EFE", "MOV"], cxestado='A'))\
            .values('cxcliente__cxcliente__ctnombre','ddeposito'
            ,'cxtipofactoring__ctabreviacion', 'dcobranza', 'nsobrepago'
            ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
            , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'C'",''))

    recuperaciones = Recuperaciones_cabecera.objects.filter(Q(cxestado='C',\
        leliminado = False) | Q(cxformacobro__in=["EFE", "MOV"], cxestado='A'))\
            .values('cxcliente__cxcliente__ctnombre','ddeposito'
            ,'cxtipofactoring__ctabreviacion', 'dcobranza', 'nsobrepago'
            ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
            , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'R'",''))

    movimiento = cobranzas.union(recuperaciones)
            
    docjson = []
    for i in range(len(movimiento)):
        docjson.append(GeneraListaCobranzasPendientesProcesarJSONSalida(movimiento[i])) 

    # docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaCobranzasPendientesProcesarJSONSalida(transaccion):
    output = {}
    output["id"] = transaccion["id"]
    output["Cliente"] = transaccion["cxcliente__cxcliente__ctnombre"]
    output["Cobranza"] = transaccion["cxcobranza"]
    output["FechaCobro"] = transaccion["dcobranza"].strftime("%Y-%m-%d")
    output["Valor"] =  transaccion["nvalor"]
    output["AplicadoCartera"] = transaccion["nvalor"] - transaccion["nsobrepago"]
    output["FormaCobro"] = transaccion["cxformapago"]
    output["TipoFactoring"] = transaccion["cxtipofactoring__ctabreviacion"]
    output["TipoOperacion"] = transaccion["tipo"]

    return output

def GeneraCargoJSONSalida(cobranza, id_cobranza, fecha_cobranza, id_asignacion
    , asignacion, id_documento, documento, dias_vencidos, dias_negociados
    , valor_cobrado, porcentaje_anticipo, base_dc, tasa_dc, dc, dcv, base_gao
    , tasa_gao, gao, base_gaoa, tasa_gaoa, gaoa, base_retenciones, retenciones
    , base_bajas, bajas):

    output = {}

    output["id_cobranza"] = id_cobranza
    output["cobranza"] = cobranza
    output["fecha_cobranza"] = fecha_cobranza.strftime("%Y-%m-%d")
    output["id_asignacion"] = id_asignacion
    output["asignacion"] = asignacion
    output["id_documento"] = id_documento
    output["documento"] = documento
    output["dias_vencidos"] = dias_vencidos
    output["dias_negociados"] =  dias_negociados
    output["valor_cobrado"] = str(round(valor_cobrado,3))
    output["porcentaje_anticipo"] = str(porcentaje_anticipo)
    output["base_dc"] = str(base_dc)
    output["tasa_dc"] = str(round(tasa_dc,3))
    output["dc"] = str(round(dc,3))
    output["dcv"] = str(round(dcv,3))
    output["base_gao"] = str(base_gao)
    output["tasa_gao"] = str(round(tasa_gao,3))
    output["gao"] = str(round(gao,3))
    output["base_gaoa"] = str(base_gaoa)
    output["tasa_gaoa"] = str(round(tasa_gaoa,3))
    output["gaoa"] = str(round(gaoa,3))
    output["base_retenciones"] = str(round(base_retenciones,3))
    output["retenciones"] = str(round(retenciones,3))
    output["base_bajas"] = str(round(base_bajas,3))
    output["bajas"] = str(round(bajas,3))

    return output

def Liquidacion(request, tipo_operacion):
    # ejecuta un store procedure 
    pslocalidad = ''

    objeto=json.loads(request.body.decode("utf-8"))
    
    psidcliente=objeto["id_cliente"]
    pdliquidacion=objeto["fecha_liquidacion"]
    pddesembolso=objeto["ddesembolso"]
    pnvalorliquidacion=objeto["valor_liquidacion"]
    pstipofactoring=objeto["tipo_factoring"]
    pnbaseiva=objeto["base_iva"]
    pnporcentajeiva=objeto["porcentaje_iva"]
    pniva=objeto["niva"]
    psinstruccionpago=objeto["sinstruccionpago"]
    padocumentos = objeto["documentos"]
    nusuario = request.user.id
    pnvuelto = objeto["vuelto"]
    pnsobrepago=objeto["sobrepago"] 
    pngao = objeto["gao"] 
    pngaoa = objeto["gaoa"]
    pndescuentodecartera =objeto["descuentodecartera"]
    pnretenciones=objeto["retenciones"]
    pnbajas = objeto["bajas"]
    pnotros = objeto["otros"]
    pnneto = objeto["neto"]
    pjcobranzas = objeto["cobranzas"]
    pjotroscargos = objeto["otros_cargos"]

    resultado=enviarPost("CALL uspLiquidarCobranzas( '{0}','{1}', {2},'{3}'\
        ,'{4}'\
        ,{5},{6},{7},{8},{9},{10}\
        ,{11},{12},{13},{14},{15},{16},'{17}'\
        ,{18},'{19}','{20}','{21}','{22}','',0)"
        .format(psidcliente ,pdliquidacion ,pnvalorliquidacion ,pstipofactoring
         ,pddesembolso\
         ,pnvuelto ,pnsobrepago ,pngao ,pngaoa,pndescuentodecartera ,pnretenciones\
         ,pnbajas ,pnotros ,pnneto,pnbaseiva ,pnporcentajeiva ,pniva ,psinstruccionpago
         ,nusuario ,padocumentos, pjcobranzas, tipo_operacion, pjotroscargos))
    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('operativos.update_asignacion', login_url='bases:sin_permisos')
def DesembolsarCobranzas(request, pk, cliente_ruc):
    template_name = "operaciones/datosdesembolsoaclientes_form.html"
    contexto = {}
    formulario={}

    cliente = Datos_generales.objects.filter(cxcliente=cliente_ruc).first()

    datosoperativos = Datos_operativos.objects.filter(cxcliente = cliente_ruc).first()
    
    cuenta_transferencia = Cuenta_transferencia.objects.cuenta_default(cliente_ruc).first()
    
    liquidacion = Liquidacion_cabecera.objects.filter(pk=pk).first()

    if request.method=="GET":

        e={'cxtipooperacion':'C'
            , 'cxoperacion':liquidacion.id
            , 'nvalor': liquidacion.nneto
            }
        formulario = DesembolsarForm(e)

        contexto={'liquidacion':liquidacion.dliquidacion
            , 'instruccion_de_pago':liquidacion.ctinstrucciondepago
            , "cuenta_transferencia":cuenta_transferencia
            , 'id_beneficiario': datosoperativos.cxbeneficiariocobranzas
            , 'beneficiario': datosoperativos.ctbeneficiariocobranzas
            , "form":formulario
            , 'cliente':cliente
            , 'tipo_operacion':'C'
            , 'operacion':liquidacion.cxliquidacion
        }

    if request.method=="POST":

        with transaction.atomic():
            # 1. Actualizar el estado de la ASIGNACION
            liquidacion.ldesembolsada = True
            liquidacion.save()

            # 2. grabar la liquidacion
            operacion = request.POST.get("cxoperacion")
            forma_pago = request.POST.get("cxformapago")

            if forma_pago =="MOV":
                cuenta_pago = None
            else:
                x = request.POST.get("cxcuentapago")
                cuenta_pago = Cuentas_bancarias.objects.filter(pk = x).first()

            if forma_pago=="CHE":
                id_beneficiario = datosoperativos.cxbeneficiarioasignacion
                beneficiario = datosoperativos.ctbeneficiarioasignacion
            else:
                id_beneficiario=None
                beneficiario=None

            if forma_pago =="TRA":
                cuenta_destino = cuenta_transferencia
            else:
                cuenta_destino = None

            liquidacion = Desembolsos(cxtipooperacion='C'
                , cxoperacion = operacion
                , cxcliente = cliente
                , nvalor = liquidacion.nneto
                , cxformapago = forma_pago
                , cxcuentapago = cuenta_pago
                , cxbeneficiario =id_beneficiario
                , ctbeneficiario = beneficiario
                , cxcuentadestino = cuenta_destino
                , cxusuariocrea = request.user
                )
            
            liquidacion.save()

        return redirect("cobranzas:listaliquidacionespendientespagar")

    return render(request, template_name, contexto)

def AceptarProtesto(request):
    # ejecuta un store procedure 
    # Devuelve el control a un proceso js

    objeto=json.loads(request.body.decode("utf-8"))

    id_cliente=objeto["id_cliente"]
    tipo_factoring=objeto["tipo_factoring"]
    forma_cobro=objeto["forma_cobro"]
    id_cobranza=objeto["id_cobranza"]
    codigo_cobranza=objeto["codigo_cobranza"]
    id_cheque=objeto["id_cheque"]
    fecha_protesto = objeto["fecha_protesto"]
    valor=objeto["valor"]
    valor_nd=objeto["valor_nd"]
    motivoprotesto=objeto["motivoprotesto"]
    tipo_emisor = objeto["tipo_emisor"]
    id_accesorio = objeto["id_accesorio"]
    tipo_operacion = objeto["tipo_operacion"]

    nusuario = request.user.id
    if id_accesorio=='':
        id_accesorio='Null'

    # Los 2 ultimos parametros son el id de cheque accesorio y el mensaje de error
    resultado=enviarPost("CALL uspRegistroProtesto( {0},'{1}',{2},'{3}','{4}'\
        ,'{5}','{6}',{7},{8},{9},{10}\
        ,'{11}',{12},'{13}','',0)"
        .format(id_cobranza, codigo_cobranza, id_cheque, id_cliente, tipo_factoring
        , forma_cobro, fecha_protesto, valor, valor_nd, motivoprotesto, nusuario
        , tipo_emisor, id_accesorio, tipo_operacion))

    return HttpResponse(resultado)

def GeneraListaProtestosPendientesJSON(request):
    # Es invocado desde la url de una tabla bt

    documentos = Cheques_protestados.objects\
        .filter(leliminado=False, nsaldo__gt = 0).all()

    tempBlogs = []
    for i in range(len(documentos)):
        tempBlogs.append(GeneraListaProtestosPendientesJSONSalida(documentos[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaProtestosPendientesJSONSalida(doc):
    output = {}
    if doc.cxtipooperacion=='C':
        cobranza = Documentos_cabecera.objects.filter(cxcheque = doc.cheque).first()
    else:
        cobranza = Recuperaciones_cabecera.objects.filter(cxcheque = doc.cheque).first()

    output['id'] = doc.id
    # los datos mostrados deben ser del cliente, no del emisor del cheque.
    output["IdCliente"] = cobranza.cxcliente.cxcliente.cxparticipante
    output["Cliente"] = cobranza.cxcliente.cxcliente.__str__()

    if doc.cxtipooperacion=='C':
        output["Cobranza"] = cobranza.cxcobranza
    else:
        output["Cobranza"] = cobranza.cxrecuperacion

    output["IdTipoFactoring"] = cobranza.cxtipofactoring.cxtipofactoring
    output["Deposito"] = cobranza.ddeposito.strftime("%Y-%m-%d")
    output["Girador"] = doc.cheque.ctgirador
    output["Cheque"] = doc.cheque.__str__()
    output["NotaDebito"] = doc.nvalornotadebito
    output["Protesto"] = doc.dprotesto
    output["Saldo"] = doc.nsaldo
    output["Motivo"] = doc.motivoprotesto.ctmotivoprotesto

    return output


def DetalleDocumentosProtesosJSON(request, ids_protestos):
    # filtrar los documentos correspondientes a la lista pasada
    documentos = Documentos_protestados.objects\
        .filter(chequeprotestado__in = ids_protestos.split(','), leliminado = False)
    
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(documentos)):
        tempBlogs.append(DocumentoProtestoJSONSalida(documentos[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DocumentoProtestoJSONSalida(doc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    # el porcenaje de anticipo se uriliza para actualizar el utilizado del cliente
    # si es accesorio el % anticipo esta en el accesorio, no en el documento.

    # los datos aqu?? van a obtenerse con el getData de la tb, aunque no se 
    # presenten en el HTML
    output = {}
    output['id'] = doc.id
    output["IdComprador"] = doc.documento.cxcomprador.cxparticipante
    output["Comprador"] = doc.documento.cxcomprador.ctnombre
    output["Asignacion"] = doc.documento.cxasignacion.cxasignacion
    output["Documento"] = doc.documento.ctdocumento
    output["Emision"] = doc.documento.demision.strftime("%Y-%m-%d")
    
    if doc.chequeprotestado.cxformacobro =="CHE":
        output["PorcentajeAnticipo"] = doc.documento.nporcentajeanticipo
        output["Vencimiento"] = doc.documento.dvencimiento
    else:
        output["PorcentajeAnticipo"] = doc.accesorio.nporcentajeanticipo
        output["Vencimiento"] = doc.accesorio.dvencimiento

    output["SaldoActual"] = doc.nsaldo
    output["Cobro"] = doc.nsaldo
    output["Bajas"] = "0.00"
    output["SaldoFinal"] = "0.0"
    output["IdProtesto"] = doc.chequeprotestado.id
    output["BajaCobranza"] = doc.nvalorbajacobranza
    output["SaldoBajaCobranza"] = doc.nsaldobajacobranza

    return output

def DatosRecuperacion(request, id, asgn, doc, sdo, cobro, baja):
    template_name = "cobranzas/datosrecuperacion_modal.html"
    contexto={
        "id": id,
        "asignacion" : asgn,
        "documento" : doc,
        "saldo" : sdo,
        "valor_cobrado": cobro,
        "baja":baja,
    }
    return render(request, template_name, contexto)

def AceptarRecuperacion(request):
    # ejecuta un store procedure 
    # Devuelve el control a un proceso js
    resultado = 'OK'
    nc=' '; gi=' '; es_cc = False; cd = 0; fd = 'Null'

    objeto=json.loads(request.body.decode("utf-8"))

    id_cliente=objeto["id_cliente"]
    tipo_factoring=objeto["tipo_factoring"]
    forma_cobro=objeto["forma_cobro"]
    fecha_cobro=objeto["fecha_cobro"]
    valor_recibido=objeto["valor_recibido"]
    sobrepago=objeto["sobrepago"]
    cuenta_bancaria = objeto["cuenta_bancaria"]
    nusuario = request.user.id
    # los siguientes son maps:
    # si debo procesar aqui uso json.loads para trabajar como diccionarios
    # si quiero enviar como parametro al store procedure paso tal cual y se recibe
    # como objeto json
    cheque = json.loads(objeto["arr_cheque"])         
    deposito=json.loads(objeto["arr_deposito"]) 
    documentos_cobrados=objeto["arr_documentos_cobrados"]

    if cheque:
        nc = cheque["numero_cheque"]
        gi = cheque["girador"]
    
    if deposito:
        cd = deposito["cuenta_deposito"]
        fd = deposito["fecha_deposito"] 

        if not cd :
            if es_cc :
                cd = 'Null'
            else:
                return HttpResponse("Debe especificar la cuenta de dep??sito")

    if not cuenta_bancaria:
        cuenta_bancaria='Null'
    
    # Los 2 ultimos parametros son el id de nueva recuperacion y el mensaje de error
    resultado=enviarPost("CALL uspAceptarRecuperacionProtesto( '{0}','{1}','{2}'\
        ,'{3}',{4},'{5}',{6},{7}\
        ,'{8}','{9}',{10},'{11}'\
        ,{12},'',0)"
        .format(id_cliente, tipo_factoring, forma_cobro
        , fecha_cobro, valor_recibido,documentos_cobrados,sobrepago,cuenta_bancaria
        ,nc, gi, cd, fd
        , nusuario))

    return HttpResponse(resultado)

def LiquidarCobranzas(request,ids_cobranzas, tipo_operacion):
    template_name = "cobranzas/datosliquidacioncobranzas_form.html"
    total_vuelto=0
    total_dc =0
    total_dcv = 0
    total_gao =0
    total_gaoa =0
    total_cargoretenciones=0
    total_cargobajas=0
    total_otroscargos=0
    total_cargos=0
    total_sobrepagos=0
    base_iva=0
    porcentaje_iva = 12
    listacargos = []
    listaotroscargos = []
    listacobranzas =[]
    vuelto_cobranza=0

    if request.method =="GET":

        if tipo_operacion=='R':
            lista_cobranzas = Recuperaciones_cabecera.objects.filter(id__in = ids_cobranzas.split(','))
        else:
            lista_cobranzas = Documentos_cabecera.objects.filter(id__in = ids_cobranzas.split(','))

        for c in range(len(lista_cobranzas)):

            cobranza = lista_cobranzas[c]

            if tipo_operacion =='R':
                detalle_cobranza = Recuperaciones_detalle.objects.filter(recuperacion = cobranza)
            else:
                detalle_cobranza = Documentos_detalle.objects.filter(cxcobranza = cobranza)

            
            cuenta_transferencia = Cuenta_transferencia\
                    .objects.cuenta_default(cobranza.cxcliente).first()
            
            datos_operativos = Datos_operativos.objects\
                        .filter(cxcliente = cobranza.cxcliente).first()

            vuelto_cobranza = 0
            # buscar el tipo de factoring
            tipofactoring = cobranza.cxtipofactoring

            for i in range(len(detalle_cobranza)):

                # inicializar
                descuento_cartera=0; descuento_cartera_vencido=0; valor_gao=0; valor_gaoa=0
                cargo_retenciones=0; cargo_bajas=0
                dias_vencidos=0; dias_negociados =0
                tasa_dc=0; tasa_gao=0;tasa_gaoa=0
                base_dc=0; base_gao=0; base_gaoa=0
                base_bajas=0; base_retenciones=0

                documento_cobrado = detalle_cobranza[i]

                # vuelto

                if tipo_operacion=='R':
                    codigo_operacion = cobranza.cxrecuperacion
                    accesorios = documento_cobrado.documentoprotestado.accesorio
                    base_bajas=documento_cobrado.nvalorbaja + documento_cobrado.nvalorbajacobranza
                else:
                    codigo_operacion = cobranza.cxcobranza
                    accesorios = cobranza.cxformapago == "DEP" 
                    base_bajas=documento_cobrado.nvalorbaja
                    base_retenciones = documento_cobrado.nretenciones

                # documento con tasas. si es accesorio las tasas etan en el accesorio
                if accesorios:
                    if tipo_operacion=='R':
                        documento = documento_cobrado.documentoprotestado.accesorio
                        vuelto = documento_cobrado.nvalorrecuperacion * (100 - documento.nporcentajeanticipo) /100
                    else:
                        documento = cobranza.cxaccesorio
                        vuelto = documento_cobrado.nvalorcobranza * (100 - documento.nporcentajeanticipo) /100

                    id_documento = documento.documento.id
                    fechadesembolso = documento.documento.cxasignacion.ddesembolso
                    asignacion = documento.documento.cxasignacion.cxasignacion
                    id_asignacion = documento.documento.cxasignacion.id
                    numero_documento = documento.documento.ctdocumento
                else:
                    # facturas puras
                    if tipo_operacion=='R':
                        documento = documento_cobrado.documentoprotestado.documento
                        vuelto = documento_cobrado.nvalorrecuperacion * (100 - documento.nporcentajeanticipo) /100
                    else:
                        documento = documento_cobrado.cxdocumento
                        vuelto = documento_cobrado.nvalorcobranza * (100 - documento.nporcentajeanticipo) /100
                    
                    id_documento = documento.id
                    fechadesembolso = documento.cxasignacion.ddesembolso
                    asignacion = documento.cxasignacion.cxasignacion
                    id_asignacion = documento.cxasignacion.id
                    numero_documento=documento.ctdocumento

                # considerar los d??as condonados
                fechacobrocalculo = cobranza.dcobranza - timedelta(days=documento_cobrado.ndiasacondonar)

                # dias vencidos
                if fechacobrocalculo > documento.dvencimiento:
                    dias_vencidos = fechacobrocalculo - documento.dvencimiento
                    dias_vencidos = dias_vencidos.days

                # generar DC
                dc = Tasas_factoring.objects.filter(cxtasa='DCAR').first()
                
                if not tipofactoring.lgeneradcenaceptacion:

                    # la tasa esta en el documento o en el accesorio
                    tasa_dc = documento.ntasadescuento

                    # dc negociado. desde desembolso hasta cobranza
                    if fechacobrocalculo > documento.dvencimiento:
                        dias_negociados = documento.dvencimiento - fechadesembolso
                    else:
                        dias_negociados = fechacobrocalculo - fechadesembolso
                    dias_negociados = dias_negociados.days

                    if dc.lsobreanticipo:
                        base_dc = documento_cobrado.aplicado() * documento.nporcentajeanticipo /100
                    else:
                        base_dc = documento_cobrado.aplicado() 
                                           
                    descuento_cartera = ( base_dc * tasa_dc / 100)

                    if not dc.lflat:
                        descuento_cartera = (descuento_cartera * dias_negociados / dc.ndiasperiocidad)


                if fechacobrocalculo > documento.dvencimiento:

                    if dc.lsobreanticipo:
                        descuento_cartera_vencido = (documento_cobrado.aplicado()
                                            * documento.nporcentajeanticipo 
                                            * documento.ntasadescuento / 10000)
                    else:
                        descuento_cartera_vencido = (documento_cobrado.aplicado	 
                                            * documento.ntasadescuento / 100)

                    if not dc.lflat:
                        descuento_cartera_vencido = (descuento_cartera_vencido 
                                                    * dias_vencidos 
                                                    / dc.ndiasperiocidad)

                # generar crgos colateral
                cargo_retenciones = base_retenciones * documento.nporcentajeanticipo / 100

                cargo_bajas = base_bajas * documento.nporcentajeanticipo / 100

                # genera GAO
                gao = Tasas_factoring.objects.filter(cxtasa="GAO").first()

                if not tipofactoring.lgeneragaoenaceptacion:

                    tasa_gao = documento.ntasacomision

                    if fechacobrocalculo > documento.dvencimiento:
                        dias_negociados = documento.dvencimiento - documento.cxasignacion.ddesembolso
                    else:
                        dias_negociados = fechacobrocalculo - documento.cxasignacion.ddesembolso

                    dias_negociados = dias_negociados.days

                    if gao.lsobreanticipo:
                        base_gao = documento_cobrado.aplicado() * documento.nporcentajeanticipo / 100
                    else:
                        base_gao = documento_cobrado.aplicado()

                    valor_gao = ( base_gao * tasa_gao / 100)

                    if not gao.lflat:
                        valor_gao = (valor_gao * dias_negociados / gao.ndiasperiocidad)


                # generar GAOA
                gaoa = Tasas_factoring.objects.filter(cxtasa="GAOA").first()

                # aplicar los d??as de gracia
                if tipofactoring.lcargagaoa and dias_vencidos > tipofactoring.ndiasgracia:

                    tasa_gaoa = datos_operativos.ntasagaoa

                    if gaoa.lsobreanticipo:
                        base_gaoa = documento_cobrado.aplicado() * documento.nporcentajeanticipo / 100
                    else:
                        base_gaoa = documento_cobrado.aplicado()

                    # si la tasa se acumula, sumarla a la tasa del documento
                    if tipofactoring.lacumulagaoaatasagao:
                        tasa_gaoa += documento.ntasacomision

                    if gaoa.lflat :
                        # determinar cuantas veces aplicar la tasa seg??n los d??as de aplicacion
                        x = math.ceil(dias_vencidos/gaoa.ndiasperiocidad)
                        tasa_gaoa = tasa_gaoa * x

                        valor_gaoa = base_gaoa * tasa_gaoa /100
                    else:
                        valor_gaoa = (base_gaoa * tasa_gaoa /100 
                                    * dias_vencidos / gaoa.ndiasperiocidad)

                # json de los cargos
                # agregar al diccionario
                listacargos.append(GeneraCargoJSONSalida(codigo_operacion, cobranza.id
                                , cobranza.dcobranza, id_asignacion, asignacion, id_documento, numero_documento
                                , dias_vencidos, dias_negociados, documento_cobrado.aplicado()
                                , documento.nporcentajeanticipo, base_dc, documento.ntasadescuento
                                , descuento_cartera, descuento_cartera_vencido, base_gao, tasa_gao
                                , valor_gao, base_gaoa, tasa_gaoa, valor_gaoa, base_retenciones
                                , cargo_retenciones, base_bajas, cargo_bajas))

                # acumula totales
                total_dc += Decimal(descuento_cartera)
                total_dcv += Decimal(descuento_cartera_vencido)
                total_gao += Decimal(valor_gao)
                total_gaoa += Decimal(valor_gaoa)
                total_cargobajas += Decimal(cargo_bajas)
                total_cargoretenciones += Decimal(cargo_retenciones)
                total_vuelto+=Decimal(vuelto)

                vuelto_cobranza += Decimal(vuelto)

            # fin del for detalle
            total_sobrepagos += cobranza.nsobrepago
            
            # arreglo de cobranzas
            output = {}

            output["cobranza"] = codigo_operacion
            output["id_cobranza"] = cobranza.id
            output["fecha_cobranza"] = cobranza.dcobranza.strftime("%Y-%m-%d")
            output["valor_cobrado"] = str(cobranza.nvalor)
            output["vuelto"] = str(vuelto_cobranza)
            output["sobrepago"] = str(cobranza.nsobrepago)
            output["total"] = str(vuelto_cobranza + cobranza.nsobrepago)

            listacobranzas.append(output)

            # si es recuperacion obtener cargos del protesto
            if tipo_operacion  == 'R':

                total_otroscargos = ObtenerCargosDeProtestos(cobranza, listaotroscargos)
            # nota:obtener cualkquier cargo cargado a la cobranza
        
        # fin for cobranzas
        # acumula base IVA de cargos
        if dc.lcargaiva: base_iva += total_dc
        if gao.lcargaiva: base_iva += total_gao
        if gaoa.lcargaiva: base_iva += total_gaoa

        total_iva = base_iva * porcentaje_iva / 100

        # Calcular neto
        total_cargos = (total_dc + total_dcv + total_gao + total_gaoa 
                        + total_cargobajas + total_cargoretenciones+ total_iva 
                        + total_otroscargos )

        neto = total_vuelto + total_sobrepagos - total_cargos


    contexto={
        "nombredecliente" : cobranza.cxcliente.cxcliente.ctnombre,
        "tipo_factoring" : tipofactoring.cxtipofactoring,
        "total_vuelto": round(total_vuelto,2),
        "total_sobrepagos": total_sobrepagos,
        "total_descuentocartera": round(total_dc + total_dcv,2),
        "total_dc": round(total_dc,2),
        "total_dcv": round(total_dcv,2),
        "total_gao": round(total_gao,2),
        "total_gaoa":round(total_gaoa,2),
        "total_iva": round(total_iva,2),
        "porcentaje_iva":porcentaje_iva,
        "total_cargoretenciones":round(total_cargoretenciones,2),
        "total_cargobajas": round(total_cargobajas,2),
        "total_otros_cargos": round(total_otroscargos,2),
        "nombre_dc": dc.ctdescripcionenreporte,
        "nombre_gao": gao.ctdescripcionenreporte,
        "nombre_gaoa": gaoa.ctdescripcionenreporte,
        "total_cargos": round(total_cargos,2),
        "neto": round(neto,2),
        'Cuentas_bancarias': CuentasEmpresa.objects.all(),
        "cuenta_transferencia":cuenta_transferencia,
        "beneficiario": datos_operativos.ctbeneficiariocobranzas,
        "data": json.dumps(listacargos),
        "form": LiquidarForm,
        "base_iva":base_iva,
        "cliente": cobranza.cxcliente.cxcliente.cxparticipante,
        "cobranzas":json.dumps(listacobranzas),
        "tipo_operacion":tipo_operacion,
        "otros_cargos":json.dumps(listaotroscargos),
    }

    return render(request, template_name, contexto)

def ObtenerCargosDeProtestos(cobranza, listaotroscargos):
    total_cargos = 0

    # Las recueracines se hacen sobre protestos, determinar los protestos
    protestos = Cheques_protestados.objects\
        .filter(id__in = Recuperaciones_detalle.objects\
            .filter(recuperacion = cobranza).values('chequeprotestado'))

    if protestos:
        for prox in protestos:
            
            # los protestos corresponden a cobranzas o recuperaciones
            if prox.cxtipooperacion=='C':
                cobranza_protestada = Documentos_cabecera.objects\
                    .filter(cxcheque = prox.cheque).first()

                codigo_operacion = cobranza_protestada.cxcobranza
            else:
                cobranza_protestada = Recuperaciones_cabecera.objects\
                    .filter(cxcheque = prox.cheque).first()

                total_cargos += ObtenerCargosDeProtestos(cobranza_protestada, listaotroscargos)
        
                codigo_operacion = cobranza_protestada.cxrecuperacion
                                
            # la nd se registra sobre la recuperacion o cobranza protestada
            nd = Notas_debito_cabecera.objects\
                .filter(cxtipooperacion = prox.cxtipooperacion
                    , operacion = cobranza_protestada.id)

            for ndx in nd:

                # el detalle de la nota de debito
                detalle_nd = Notas_debito_detalle.objects\
                    .filter(notadebito = ndx)

                for detallex in detalle_nd:

                    # los cargos indicados en el detalle de la nd
                    cargos = Cargos_detalle.objects\
                        .filter(id = detallex.cargo.id )

                    for cargo in cargos:
                        
                        listaotroscargos.append(GeneraOtroCargoJSONSalida(
                            cargo.id, cargo.cxmovimiento.ctmovimiento
                            , cargo.dregistro, cargo.nsaldo, ndx.id
                            , codigo_operacion))

                        total_cargos += cargo.nsaldo
        return total_cargos

def GeneraOtroCargoJSONSalida(id_cargo, nombre_cargo, fecha,  valor
                            , id_nd, codigo_operacion):

    output = {}

    output["id_cargo"] = id_cargo
    output["id_nd"] = id_nd
    output["descripcion"] = nombre_cargo
    output["codigo_cobranza"] = codigo_operacion
    # output["tipo_operacion"] = tipo_operacion
    # output["id_operacion"] = id_nd
    output["fecha"] = fecha.strftime("%Y-%m-%d")
    output["valor"] = str(round(valor,2))

    return output

def ReversaLiquidacion(request, pid_liquidacion,codigo_liquidacion,tipo_operacion):
    # # ejecuta un store procedure 
    nusuario = request.user.id
    resultado=enviarPost("CALL uspReversaLiquidarCobranzas( {0},'{1}','{2}',{3},'')"
    .format(pid_liquidacion,codigo_liquidacion,tipo_operacion, nusuario))

    return HttpResponse(resultado)

def ReversaCobranza(request, pid_cobranza, tipo_operacion):
    # ejecuta un store procedure 
    #  EL TIPO DE OPERACION debe determinar el SP a ejecutar: o cobranzas o recuperaciones
    nusuario = request.user.id
    
    if tipo_operacion[0]=='C':
        resultado=enviarPost("CALL uspReversarCobranzaCartera( {0},{1},'')"
        .format(pid_cobranza, nusuario))
    elif tipo_operacion[0]=='R':
        resultado='falta sp reverso recuperaciones'
    

    return HttpResponse(resultado)

def GeneraListaCobranzasRegistradasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt
    if desde == 'None':
        cobranzas = Documentos_cabecera.objects.all()\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                ,'cxcheque', 'cxestado', 'dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
        recuperaciones = Recuperaciones_cabecera.objects.all()\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro'
                ,'nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))
    else:

        cobranzas = Documentos_cabecera.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
                
        recuperaciones = Recuperaciones_cabecera.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))

    movimiento = cobranzas.union(recuperaciones, )
            
    tempBlogs = []
    for i in range(len(movimiento)):
        tempBlogs.append(GeneraListaCobranzasJSONSalida(movimiento[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)
