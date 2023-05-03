from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q
from django.db.models.expressions import RawSQL 

from .models import Documentos_cabecera, Documentos_detalle, Liquidacion_cabecera\
    , Cheques_protestados, Cheques, Recuperaciones_cabecera\
    , Documentos_protestados, Recuperaciones_detalle, Cargos_cabecera
from operaciones.models import Documentos, ChequesAccesorios, Datos_operativos\
    , Desembolsos, Motivos_protesto_maestro, Cargos_detalle, Notas_debito_cabecera\
    , Notas_debito_detalle, Cheques_canjeados, Cheques_quitados, Ampliaciones_plazo_cabecera
from clientes.models import Cuentas_bancarias, Datos_generales\
    , Cuenta_transferencia, Datos_compradores
from empresa.models import Tasas_factoring, Cuentas_bancarias as CuentasEmpresa\
    , Datos_participantes, Tipos_factoring
from cuentasconjuntas import models as CuentasConjuntasModels
from bases.models import Usuario_empresa

from .forms import CobranzasDocumentosForm, ChequesForm, LiquidarForm\
    , MotivoProtestoForm, ProtestoForm, RecuperacionesProtestosForm\
    , CobranzasCargosForm, AccesoriosForm

from operaciones.forms import DesembolsarForm

from datetime import date, timedelta
from decimal import Decimal

import json
import math

from bases.views import enviarPost, numero_a_letras

FACTURAS_PURAS = 'F'
FACTURAS_CON_ACCESORIOS = 'A'

class DocumentosVencidosView(LoginRequiredMixin, generic.ListView):
    model = Documentos
    template_name = "cobranzas/listadocumentospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Documentos.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self,*args, **kwargs): 
        context = super(DocumentosVencidosView, self).get_context_data(*args,**kwargs) 
        fecha_corte = date.today() 
        context['fecha_corte'] =  fecha_corte
        context['por_vencer'] = 'No'

        return context

class DocumentosPorVencerView(LoginRequiredMixin, generic.ListView):
    model = Documentos
    template_name = "cobranzas/listadocumentospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Documentos.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self,*args, **kwargs): 
        context = super(DocumentosPorVencerView, self).get_context_data(*args,**kwargs) 
        fecha_corte = date.today() + timedelta(days=7)
        context['fecha_corte'] =  fecha_corte
        context['por_vencer'] = 'Si'

        return context

class ChequesADepositarView(LoginRequiredMixin, generic.ListView):
    # la lista se obtiene desde url en la tabla bt, 
    # el model indicado es solo para fluir con el django. No se usa.
    model = ChequesAccesorios
    template_name = "cobranzas/listachequesadepositar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=ChequesAccesorios.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self,*args, **kwargs): 
        context = super(ChequesADepositarView, self).get_context_data(*args,**kwargs) 
        fecha_corte = date.today() 
        context['fecha_corte'] =  fecha_corte#.strftime("%Y-%m-%d")

        return context

class CobranzasDocumentosView(LoginRequiredMixin, generic.FormView):
    model = Documentos_cabecera
    # en esta vista el id del cliente es el correspondiente a la tabla clientes
    # el id del comprador es el que corresponde a la tabla comprador

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
        cliente_id = self.kwargs.get('cliente_ruc')
        un_solo_deudor = self.kwargs.get('un_comprador')
        deudor_id = self.kwargs.get('deudor_id')
        tipo_factoring = self.kwargs.get('tipo_factoring')
        por_vencer = self.kwargs.get('por_vencer')

        cliente = Datos_generales.objects\
            .filter(id = cliente_id).first()

        cuentas = Cuentas_bancarias\
            .objects.filter(cxparticipante = cliente.cxcliente.id \
                , leliminado = False, lpropia = True).all()
                # , cxtipocuenta = 'C').all()
        cuentas_deudor = None

        if un_solo_deudor=="Si":
            comprador = Datos_compradores.objects\
                .filter(id = deudor_id).first()

            cuentas_deudor = Cuentas_bancarias\
                .objects.filter(cxparticipante = comprador.cxcomprador.id \
                    , leliminado = False, lpropia = True).all()
                    # , cxtipocuenta = 'C').all()   # podría hacer transferencias desde cuenta de ahorros

        cuentas_conjuntas = CuentasConjuntasModels.Cuentas_bancarias\
            .objects.filter(cxcliente = cliente_id \
                , leliminado = False, lactiva = True).all()

        context = super(CobranzasDocumentosView, self).get_context_data(**kwargs)
        context["documentos"] = docs
        context["total_cartera"] = total_cartera
        context["forma_cobro"] = forma_cobro
        context["form_cheque"] = ChequesForm
        context["cuentas_bancarias_cliente"] = cuentas
        context["cuentas_bancarias_deudor"] = cuentas_deudor
        context["un_solo_comprador"] = un_solo_deudor
        context["cliente_id"] = cliente_id
        context["cliente"] = cliente
        context["tipo_factoring"] = tipo_factoring
        context["deudor_id"] = deudor_id
        context["cuentas_conjuntas"] = cuentas_conjuntas
        context["tipo"]="Cobranza"
        context["por_vencer"]=por_vencer
        return context

class CobranzasConsulta(LoginRequiredMixin, generic.ListView):
    model = Documentos_cabecera
    template_name = "cobranzas/consultageneralcobranzas.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Documentos_cabecera.objects.filter(leliminado = False
                                              , empresa = id_empresa.empresa
                                              )
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()

        context = super(CobranzasConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] =hasta
        return context
 
class CobranzasPorConfirmarView(LoginRequiredMixin, generic.ListView):
    # la lista se obtiene desde url en la tabla bt, 
    # el model indicado es solo para fluir con el django. No se usa.
    model = Documentos_cabecera
    template_name = "cobranzas/listacobranzasporconfirmar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        cobranzas = Documentos_cabecera.objects.filter(cxestado='A'\
            , leliminado = False\
            , cxformapago__in = ['TRA','CHE','DEP']\
            , empresa = id_empresa.empresa
            , cxtipofactoring__lanticipatotalnegociado = False )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','ldepositoencuentaconjunta'
                ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'C'",'')
                )
                
        recuperaciones = Recuperaciones_cabecera.objects.filter(cxestado='A'\
            , leliminado = False\
            , cxformacobro__in = ['TRA','CHE']\
            , empresa = id_empresa.empresa
            , cxtipofactoring__lanticipatotalnegociado = False )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','ldepositoencuentaconjunta'
                ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'R'",'')
                )

        return cobranzas.union(recuperaciones)

class CobranzasPendientesLiquidarView(LoginRequiredMixin, generic.ListView):
    model = Documentos_cabecera
    template_name = "cobranzas/listacobranzaspendientesliquidar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        cobranzas= Documentos_cabecera.objects.filter(Q(cxestado='C'\
            , empresa = id_empresa.empresa
            , leliminado = False) | Q(cxformapago__in=["EFE", "MOV"], cxestado='A'))\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion'
                ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'C'",''))

        recuperaciones = Recuperaciones_cabecera.objects.filter(Q(cxestado='C'\
            , empresa = id_empresa.empresa
            , leliminado = False) | Q(cxformacobro__in=["EFE", "MOV"], cxestado='A'))\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion'
                ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
                , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'R'",''))

        return cobranzas.union(recuperaciones)

class LiquidacionesPendientesPagarView(LoginRequiredMixin, generic.ListView):
    model = Liquidacion_cabecera
    template_name = "cobranzas/listaliquidacionespendientespagar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        return Liquidacion_cabecera.objects.filter(ldesembolsada=False\
            , empresa = id_empresa.empresa
            , leliminado = False, ddesembolso__lte = date.today())

class MotivosProtestoView(LoginRequiredMixin, generic.ListView):
    model = Motivos_protesto_maestro
    template_name = "cobranzas/listamotivosprotesto.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Motivos_protesto_maestro.objects.filter(leliminado = False
                                              , empresa = id_empresa.empresa
                                              )
        return qs

class MotivoProtestoNew(LoginRequiredMixin, generic.CreateView):
    model = Motivos_protesto_maestro
    template_name = "cobranzas/datosmotivoprotesto_form.html"
    form_class = MotivoProtestoForm
    context_object_name='motivo'
    success_url= reverse_lazy("cobranzas:listamotivosprotesto")
    login_url = 'bases:login'

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
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
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_cheque = self.kwargs.get('id_cheque')
        id_cobranza = self.kwargs.get('id_cobranza')
        lista_deposito =self.kwargs.get('lista_deposito')

        cheque = Cheques.objects.filter(pk=id_cheque).first()
        cobranza = Documentos_cabecera.objects.filter(pk = id_cobranza).first()

        # Call the base implementation first to get a context
        context = super(ProtestoCobranzaNew, self).get_context_data(**kwargs)
        context["cheque"]=cheque
        context["cobranza"] = cobranza
        context["id_cliente"] = cobranza.cxcliente.id
        context["forma_cobro"] = cobranza.cxformapago
        context["codigo_cobranza"] = cobranza.cxcobranza
        context["tipo_operacion"]='Cobranza'
        context["lista_deposito"]=lista_deposito

        return context

class ProtestosPendientesView(LoginRequiredMixin, generic.ListView):
    model = Cheques_protestados
    template_name = "cobranzas/listaprotestospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Cheques_protestados.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

class RecuperacionProtestoView(LoginRequiredMixin, generic.FormView):
    model = Recuperaciones_cabecera
    # 31-ene-23 l.g.    usar la misma forma de cobranzas
    # en esta vista el id del cliente es el correspondiente a la tabla participante
    # el id del comprador es el que corresponde a la tabla participante

    template_name = "cobranzas/datoscobranzas_form.html"
    context_object_name='cobranza'
    login_url = 'bases:login'
    form_class = RecuperacionesProtestosForm

    # recibe como parametros los id's de los protestos a cobrar
    # los pasa al html para que se pasen al js que carga el detalle
    def get_context_data(self, **kwargs):

        docs = self.kwargs.get('ids_protestos')
        total_cartera=self.kwargs.get('total_cartera')
        forma_cobro=self.kwargs.get('forma_cobro')
        cliente_id = self.kwargs.get('cliente_ruc')
        un_solo_deudor = self.kwargs.get('un_comprador')
        deudor_id = self.kwargs.get('deudor_id')
        tipo_factoring = self.kwargs.get('tipo_factoring')
        # nota: debe tomar del tipo de factoring el con o sin recurso
        modalidad_factoring='CR'

        cliente = Datos_participantes.objects\
            .filter(pk = cliente_id).first()

        cuentas = Cuentas_bancarias\
            .objects.filter(cxparticipante = cliente_id \
                , leliminado = False, lpropia = True).all()
                # , cxtipocuenta = 'C').all()
        cuentas_deudor = None

        if un_solo_deudor=="Si":
            cuentas_deudor = Cuentas_bancarias\
                .objects.filter(cxparticipante = deudor_id \
                    , leliminado = False, lpropia = True).all()
                    # , cxtipocuenta = 'C').all()   # podría hacer transferencias desde cuenta de ahorros

        cuentas_conjuntas = CuentasConjuntasModels.Cuentas_bancarias\
            .objects.filter(cxcliente = cliente.datos_generales.id \
                , leliminado = False, lactiva = True).all()


        # Call the base implementation first to get a context
        context = super(RecuperacionProtestoView, self).get_context_data(**kwargs)
        context["documentos"] = docs
        context["total_cartera"] = total_cartera
        context["forma_cobro"] = forma_cobro
        context["form_cheque"] = ChequesForm
        context["cuentas_bancarias_cliente"] = cuentas
        context["cliente_id"] = cliente_id
        context["cliente"] = cliente
        context["tipo_factoring"] = tipo_factoring
        context["cuentas_bancarias_deudor"] = cuentas_deudor
        context["un_solo_comprador"] = un_solo_deudor
        context["deudor_id"] = deudor_id
        context["cuentas_conjuntas"] = cuentas_conjuntas
        context["tipo"]="Recuperación"

        return context

class ProtestoRecuperacionNew(LoginRequiredMixin, generic.CreateView):
    model=Cheques_protestados
    template_name="cobranzas/datosprotesto_form.html"
    context_object_name = "consulta"
    form_class=ProtestoForm
    success_url=reverse_lazy("cobranzas:listacobranzasporconfirmar")
    success_message="Protesto creada satisfactoriamente"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_cheque = self.kwargs.get('id_cheque')
        id_cobranza = self.kwargs.get('id_cobranza')
        lista_deposito =self.kwargs.get('lista_deposito')

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
        context["lista_deposito"]=lista_deposito

        return context

class LiquidacionesEnNegativoPendientesView(LoginRequiredMixin, generic.ListView):
    model = Notas_debito_cabecera
    template_name = "cobranzas/listaliquidacionesennegativo.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        return Notas_debito_cabecera.objects\
        .filter(cxtipooperacion__in = 'LCRB', leliminado = False
                , empresa = id_empresa.empresa
                , nsaldo__gt = 0)

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(LiquidacionesEnNegativoPendientesView, self).get_context_data(**kwargs)
        context["tipo_nd"] = 'ND'

        return context

class CobranzasCargosView(LoginRequiredMixin, generic.FormView):
    model = Cargos_cabecera
    template_name = "cobranzas/datoscobranzascargos_form.html"
    context_object_name='cobranza'
    login_url = 'bases:login'
    form_class = CobranzasCargosForm

    # recibe como parametros los id's de los documentos a cobrar
    # los pasa al html para que se pasen al js que carga el detalle
    def get_context_data(self, **kwargs):

        docs = self.kwargs.get('ids_documentos')
        total_cartera=self.kwargs.get('total_cargos')
        forma_cobro=self.kwargs.get('forma_cobro')
        cliente_id = self.kwargs.get('cliente_id')
        tipo_factoring = self.kwargs.get('tipo_factoring')
        tipo_nd = self.kwargs.get('tipo_nd')

        cliente = Datos_generales.objects.filter(id = cliente_id).first()

        cuentas = Cuentas_bancarias\
            .objects.filter(cxparticipante = cliente.cxcliente \
                , leliminado = False, lpropia = True).all()
                # , cxtipocuenta = 'C').all()
        
        # Call the base implementation first to get a context
        context = super(CobranzasCargosView, self).get_context_data(**kwargs)
        context["documentos"] = docs
        context["total_cargos"] = total_cartera
        context["forma_cobro"] = forma_cobro
        context["form_cheque"] = ChequesForm
        context["cuentas_bancarias_cliente"] = cuentas
        context["cliente_id"] = cliente_id
        context["cliente"] = cliente
        context["tipo_factoring"] = tipo_factoring
        context["tipo_nd"] = tipo_nd

        return context

class AmpliacionesDePlazoPendientesView(LoginRequiredMixin, generic.ListView):
    model = Notas_debito_cabecera
    template_name = "cobranzas/listaampliacionesdeplazopendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        return Notas_debito_cabecera.objects\
        .filter(cxtipooperacion = 'A', leliminado = False
                , empresa = id_empresa.empresa
                , nsaldo__gt = 0)
    
    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(AmpliacionesDePlazoPendientesView, self).get_context_data(**kwargs)
        context["tipo_nd"] = 'AP'

        return context

def CobranzaPorCondonar(request,pk, tipo_operacion):
    template_name = "cobranzas/detallecobroporcondonar.html"
    
    if tipo_operacion=='C':
        operacion = Documentos_cabecera.objects.filter(pk=pk).first()
        
    else:
        operacion = Recuperaciones_cabecera.objects.filter(pk=pk).first()
        
    contexto={"operacion": operacion
        , "tipo_operacion": tipo_operacion
        }
    
    return render(request, template_name, contexto)

def GeneraListaCarteraPorVencerJSON(request, fecha_corte = None):
    # Es invocado desde la url de una tabla bt
    # if not fecha_corte: 
    #     fecha = date.today()
    #     fecha = fecha + timedelta(days=7)
    # Se incluyen los registros de cheques a los que se le quitó el acesorio
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    tempBlogs = []
    documentos = Documentos.objects.facturas_pendientes(fecha_corte
                                                        , id_empresa.empresa).all()

    for i in range(len(documentos)):
        tempBlogs.append(GeneraListaCarterPorVencerJSONSalida(documentos[i])) 

    # los accesorios que fueron quitados se convierten en facturas pendientes
    quitados = ChequesAccesorios.objects.facturas_pendientes(fecha_corte
                                                             , id_empresa.empresa).all()

    for i in range(len(quitados)):
        tempBlogs.append(GeneraListaAccesoriosQuitadosJSONSalida(quitados[i])) 

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
    output["IdCliente"] = doc.cxcliente.id
    output["Cliente"] = doc.cxcliente.cxcliente.ctnombre
    output["IdComprador"] = doc.cxcomprador.id
    output["Comprador"] = doc.cxcomprador.cxcomprador.ctnombre
    output["IdTipoFactoring"] = doc.cxtipofactoring.id
    output["TipoFactoring"] = doc.cxtipofactoring.ctabreviacion
    output["Asignacion"] = doc.cxasignacion.cxasignacion
    output["Documento"] = doc.ctdocumento
    output["Vencimiento"] = doc.vencimiento().strftime("%Y-%m-%d")
    output["Saldo"] = doc.nsaldo
    if doc.dultimacobranza:
        output["UltimaCobranza"] = doc.dultimacobranza.strftime("%Y-%m-%d")
    else:
        output["UltimaCobranza"] =''
    output["Anticipa100"] = doc.cxtipofactoring.lanticipatotalnegociado
    output["Tipo_asignacion"] = 'F'
    
    return output

def GeneraListaAccesoriosQuitadosJSONSalida(acc):
    output = {}
    # para diferenciar de facturas puras usar un indice negativo
    output['id'] = -acc.id
    output["IdCliente"] = acc.documento.cxcliente.id
    output["Cliente"] = acc.documento.cxcliente.cxcliente.ctnombre
    output["IdComprador"] = acc.documento.cxcomprador.id
    output["Comprador"] = acc.documento.cxcomprador.cxcomprador.ctnombre
    output["IdTipoFactoring"] = acc.documento.cxtipofactoring.id
    output["TipoFactoring"] = acc.documento.cxtipofactoring.ctabreviacion
    output["Asignacion"] = acc.documento.cxasignacion.cxasignacion
    output["Documento"] = acc.documento.ctdocumento
    output["Vencimiento"] = acc.vencimiento().strftime("%Y-%m-%d")
    output["Saldo"] = acc.chequequitado.nsaldo
    if acc.chequequitado.dultimacobranza:
        output["UltimaCobranza"] = acc.chequequitado.dultimacobranza.strftime("%Y-%m-%d")
    else:
        output["UltimaCobranza"] =''

    output["Anticipa100"] = acc.documento.cxtipofactoring.lanticipatotalnegociado
    output["Tipo_asignacion"] = 'A'

    return output

def DetalleDocumentosFacturasPuras(request, ids_documentos):
    # filtrar los documentos correspondientes a la lista pasada
    arr_acc = []
    arr_fac = []
    tempBlogs = []

    ids = ids_documentos.split(',')
    for id in ids:
        if int(id) < 0:
            arr_acc.append(-int(id))
        else:
            arr_fac.append(id)

    documentos = Documentos.objects.filter(id__in = arr_fac, leliminado = False)
    
    for id in range(len(documentos)):
        tempBlogs.append(GeneraListaDocumentosSeleccionadosOutput(documentos[id])) # Converting `QuerySet` to a Python Dictionary

    quitados = ChequesAccesorios.objects.filter(id__in = arr_acc, leliminado = False)

    for i in range(len(quitados)):
        tempBlogs.append(GeneraListaAccesoriosQuitadosSeleccionadosOutput(quitados[i])) 

    docjson = tempBlogs

    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def GeneraListaDocumentosSeleccionadosOutput(doc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    # los datos aquí van a obtenerse con el getData de la tb, aunque no se 
    # presenten en el HTML
    output = {}
    output['id'] = doc.id
    output["IdComprador"] = doc.cxcomprador.id
    output["Comprador"] = doc.cxcomprador.cxcomprador.ctnombre
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
    output["AccesorioQuitado"] = None

    return output

def GeneraListaAccesoriosQuitadosSeleccionadosOutput(acc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    # los datos aquí van a obtenerse con el getData de la tb, aunque no se 
    # presenten en el HTML
    output = {}
    output['id'] = acc.documento.id
    output["IdComprador"] = acc.documento.cxcomprador.id
    output["Comprador"] = acc.documento.cxcomprador.cxcomprador.ctnombre
    output["Asignacion"] = acc.documento.cxasignacion.cxasignacion
    output["Documento"] = acc.documento.ctdocumento
    output["Emision"] = acc.documento.demision.strftime("%Y-%m-%d")
    output["PorcentajeAnticipo"] = acc.nporcentajeanticipo
    output["Vencimiento"] = acc.dvencimiento.strftime("%Y-%m-%d")
    output["SaldoActual"] = acc.chequequitado.nsaldo
    output["Cobro"] = acc.chequequitado.nsaldo
    output["Retenido"] = "0.0"
    output["Bajas"] = "0.00"
    output["SaldoFinal"] = "0.0"
    output["AccesorioQuitado"] = acc.chequequitado.id

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
    nc=' '; gi=' '; es_cc = False; cd = 'Null'; fd = 'Null'; cc='Null'

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
        cc = deposito["cuenta_conjunta"]
        fd = "'"  + deposito["fecha_deposito"] + "'"

        if not cd :
            if es_cc :
                cd = 'Null'
            else:
                return HttpResponse("Debe especificar la cuenta de depósito")
        else:
            cc='Null'

    if not cuenta_bancaria:
        cuenta_bancaria='Null'
    
    # Los 2 ultimos parametros son el id de cheque accesorio y el mensaje de error
    resultado=enviarPost("CALL uspAceptarCobranzaCartera( '{0}','{1}','{2}','{3}'\
        ,{4},{5},{6},{7}\
        ,'{8}','{9}',{10},{11},{12}\
        ,'{13}', '{14}',{15},Null,{16},'',0)"
        .format(id_cliente, tipo_factoring, forma_cobro, fecha_cobro
        , valor_recibido, pagador_por_cliente, sobrepago, cuenta_bancaria
        ,nc,gi,es_cc, cd, fd
        ,documentos_cobrados, id_deudor,nusuario, cc))

    return HttpResponse(resultado)

def GeneraListaChequesADepositarJSON(request, fecha_corte):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    documentos = ChequesAccesorios.objects\
        .cheques_a_depositar(fecha_corte, id_empresa.empresa).all()

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
    output["IdCliente"] = doc.documento.cxcliente.id
    output["Cliente"] = doc.documento.cxcliente.cxcliente.ctnombre
    output["IdComprador"] = doc.documento.cxcomprador.id
    output["Comprador"] = doc.documento.cxcomprador.cxcomprador.ctnombre
    output["IdTipoFactoring"] = doc.documento.cxtipofactoring.id
    output["TipoFactoring"] = doc.documento.cxtipofactoring.ctabreviacion
    output["Asignacion"] = doc.documento.cxasignacion.cxasignacion
    output["Documento"] = doc.documento.ctdocumento
    output["Vencimiento"] = doc.vencimiento().strftime("%Y-%m-%d")
    output["Valor"] = doc.ntotal
    output["Datos"] = doc.cxbanco.ctbanco +' CTA.'+ doc.ctcuenta + ' CH/' + doc.ctcheque
    output["Anticipa100"] = doc.documento.cxtipofactoring.lanticipatotalnegociado

    return output

def DepositoCheques(request, ids_cheques, total_cartera, cuenta_destino
                    , id_cliente=None):
    template_name = "cobranzas/depositocheques_form.html"
    contexto={}
    result={}
    cuentas_conjuntas=None

    if request.method =='GET':

        result = (ChequesAccesorios.objects.filter(id__in = ids_cheques.split(','))
            .values( 'documento__cxcliente__cxcliente__ctnombre')
            .annotate(pcount=Count('documento'))
            .annotate(total = Sum('ntotal'))
            .order_by()
        )        
        if cuenta_destino=='CC':
            cuentas_conjuntas = CuentasConjuntasModels.Cuentas_bancarias\
                .objects.filter(cxcliente = id_cliente , leliminado = False
                                , lactiva = True)\
                .all()

    contexto = {"cheques" : result
        , "total_cartera" : total_cartera
        , "form": CobranzasDocumentosForm
        , "cuenta_destino" : cuenta_destino
        , "cuentas_conjuntas": cuentas_conjuntas
        }

    if request.method == 'POST':

        # si cuenta de destino es de la empresa:
        if cuenta_destino=='CE':
            cd=request.POST.get("cxcuentadeposito")
            cc='Null'
        else:
        # si cuenta de destino es del cliente
            cc=request.POST.get("cuenta_conjunta")
            cd='Null'

        fd=request.POST.get("ddeposito")

        resultado=enviarPost("CALL uspDepositarChequesAccesorios( '{0}',{1},'{2}'\
            ,{3},{4},'')"
            .format(ids_cheques,cd, fd, request.user.id, cc))

        if resultado[0] !='OK':
            return HttpResponse(resultado)

        return redirect("cobranzas:listachequesadepositar")


    return render(request, template_name, contexto)

def GeneraListaCobranzasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        cobranzas = Documentos_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                ,'cxcheque', 'cxestado', 'dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
        
        recuperaciones = Recuperaciones_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro'
                ,'nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))
        
        protestos_cobranzas = Documentos_cabecera.objects\
            .filter(cxestado='P', empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C protestada'",''))
        
        protestos_recuperaciones = Recuperaciones_cabecera.objects\
            .filter(cxestado='P', empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R protestada'",''))
        
        cargos = Cargos_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'CC'",''))
        
        liquidaciones = Liquidacion_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddesembolso'
                ,'cxtipofactoring__ctabreviacion','cxliquidacion'
                ,'jcobranzas'
                ,'nneto', 'dliquidacion'
                , 'nneto', 'cxtipofactoring','dregistro'
                , 'id', 'nneto','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'L'",''))
    else:

        cobranzas = Documentos_cabecera.objects\
            .filter(dcobranza__gte = desde
                    , empresa = id_empresa.empresa
                    , dcobranza__lte = hasta)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
                
        recuperaciones = Recuperaciones_cabecera.objects\
            .filter(dcobranza__gte = desde
                    , empresa = id_empresa.empresa
                    , dcobranza__lte = hasta)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))

        protestos_cobranzas = Documentos_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta
                    , empresa = id_empresa.empresa
                    , cxestado='P')\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C protestada'",''))
                    
        protestos_recuperaciones = Recuperaciones_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta
                    , empresa = id_empresa.empresa
                    , cxestado='P')\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxcheque__cheque_protestado__motivoprotesto__ctmotivoprotesto'
                ,'nvalor', 'cxcheque__cheque_protestado__dprotesto'
                ,'cxcheque', 'cxcheque__cheque_protestado__cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R protestada'",''))

        cargos = Cargos_cabecera.objects\
            .filter(dcobranza__gte = desde, dcobranza__lte = hasta
                    , empresa = id_empresa.empresa
                    )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'CC'",''))

        liquidaciones = Liquidacion_cabecera.objects\
            .filter(dliquidacion__gte = desde, dliquidacion__lte = hasta
                    , empresa = id_empresa.empresa
                    )\
                .values('cxcliente__cxcliente__ctnombre','ddesembolso'
                ,'cxtipofactoring__ctabreviacion','cxliquidacion'
                ,'ctinstrucciondepago'
                ,'nneto', 'dliquidacion'
                , 'nneto', 'cxestado','dregistro'
                , 'id', 'nneto','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'L'",''))

    movimiento = cobranzas.union(recuperaciones, protestos_cobranzas
        , protestos_recuperaciones, cargos, liquidaciones).order_by('dcobranza')

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

    if 'protestada' in transaccion['tipo'] or transaccion['tipo']=='L':
        output["Detalle"] = transaccion['cxformapago']
    else:
        if transaccion['cxformapago'] =="CHE" or transaccion['cxformapago'] =="DEP":
            cheque = Cheques.objects.filter(pk = transaccion['cxcheque']).first()
            output["Detalle"] = cheque.__str__()
        elif transaccion['cxformapago'] =="TRA":
            cuenta = Cuentas_bancarias.objects\
                .filter(pk = transaccion['cxcuentatransferencia']).first()
            output["Detalle"] = cuenta.__str__()

        output["FormaCobro"] = transaccion['cxformapago']
        if transaccion['ddeposito']:
            output["Deposito"] = transaccion['ddeposito'].strftime("%Y-%m-%d")
        output["Sobrepago"] = transaccion['nsobrepago']

    if transaccion['tipo'] =='C':
        output["Movimiento"] = 'Cobranza'
    elif transaccion['tipo'] =='R':
        output["Movimiento"] = 'Recuperación'
    elif transaccion['tipo'] =='C protestada':
        output["Movimiento"] = 'Protesto de cobranza'
    elif transaccion['tipo'] =='R protestada':
        output["Movimiento"] = 'Protesto de recuperación'
    elif transaccion['tipo'] =='CC':
        output["Movimiento"] = 'Cobranza de cargos'
    elif transaccion['tipo'] =='L':
        output["Movimiento"] = 'Liquidación'

    # se necesita el tipo de operacion para saber que va a imprimir o reversar
    output["TipoOperacion"] = transaccion["tipo"]
    # output["FormaPago"] = transaccion["cxformapago"]

    return output

@login_required(login_url='/login/')
@permission_required('cobranzas.update_documentos_cabecera', login_url='bases:sin_permisos')
def ConfirmarCobranza(request, cobranza_id, tipo_operacion):

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
    output["Comprador"] = doc.cxdocumento.cxcomprador.cxcomprador.ctnombre
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
    output["Comprador"] = doc.documentoprotestado.documento.cxcomprador.cxcomprador.ctnombre
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
            return "cobranza/recuperación no encontrada"

        return redirect("cobranzas:cobranzaporcondonar", pk=cobranza_id, tipo_operacion=tipo_operacion)
        
        
    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('cobranzas.update_documentos_cabecera', login_url='bases:sin_permisos')
def ReversaConfirmacionCobranza(request, cobranza_id, tipo_operacion):
    # la eliminacion es lógica
    # debe devolver: OK si esta bien

    if tipo_operacion =='C':
        cobr = Documentos_cabecera.objects.filter(pk=cobranza_id).first()
        if not cobr:
            return HttpResponse("Cobranza no encontrada")
        operacion = cobr.cxcobranza

    else:
        cobr = Recuperaciones_cabecera.objects.filter(pk=cobranza_id).first()
        if not cobr:
            return HttpResponse("Recuperación no encontrada")
        operacion = cobr.cxrecuperacion


    if request.method=="GET":
        cobr.cxestado = "A"
        cobr.save()
        # SI es cobranza en cuenta conjunta debe borrarse el movimiento de la operacion
        # para borrar necesito la id de cuenta conjunta y codigo de cobranza
        if cobr.ldepositoencuentaconjunta:
            cc = cobr.cxcuentaconjunta
            movimiento_cc = CuentasConjuntasModels.Movimientos.objects\
                .filter(cxmovimiento = operacion, cxtipo = tipo_operacion, cuentabancaria = cc)\
                    .first()
            if movimiento_cc:
                movimiento_cc.leliminado = True
                movimiento_cc.cxusuarioelimina = request.user.id
                movimiento_cc.save()



    return HttpResponse("OK")

def GeneraListaCobranzasPendientesProcesarJSON(request):
    # Es invocado desde la url de una tabla bt
    # son liquidables las que están confirmadas ademas de los cobros en efectivo y
    # movimientos contables
    # movimiento = Documentos_cabecera.objects.filter(Q(cxestado='C',\
    #         leliminado = False) | Q(cxformapago__in=["EFE", "MOV"], cxestado='A'))

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    cobranzas= Documentos_cabecera.objects\
        .filter(Q(cxestado='C', empresa = id_empresa.empresa\
                  ,leliminado = False) | Q(cxformapago__in=["EFE", "MOV"]
                                           , cxestado='A'))\
            .values('cxcliente__cxcliente__ctnombre','ddeposito'
            ,'cxtipofactoring__ctabreviacion', 'dcobranza', 'nsobrepago'
            ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
            , 'id', 'cxcheque_id','cxcliente').annotate(tipo=RawSQL("select 'C'",''))

    recuperaciones = Recuperaciones_cabecera.objects\
        .filter(Q(cxestado='C', empresa = id_empresa.empresa\
                  ,leliminado = False) | Q(cxformacobro__in=["EFE", "MOV"]
                                           , cxestado='A'))\
            .values('cxcliente__cxcliente__ctnombre','ddeposito'
            ,'cxtipofactoring__ctabreviacion', 'dcobranza', 'nsobrepago'
            ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
            , 'id', 'cxcheque_id','cxcliente').annotate(tipo=RawSQL("select 'R'",''))

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
    output["IdCliente"] = transaccion["cxcliente"]
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
    output["valor_cobrado"] = str(round(valor_cobrado,2))
    output["porcentaje_anticipo"] = str(porcentaje_anticipo)
    output["base_dc"] = str(base_dc)
    output["tasa_dc"] = str(round(tasa_dc,2))
    output["dc"] = str(round(dc,2))
    output["dcv"] = str(round(dcv,2))
    output["base_gao"] = str(base_gao)
    output["tasa_gao"] = str(round(tasa_gao,2))
    output["gao"] = str(round(gao,2))
    output["base_gaoa"] = str(base_gaoa)
    output["tasa_gaoa"] = str(round(tasa_gaoa,2))
    output["gaoa"] = str(round(gaoa,2))
    output["base_retenciones"] = str(round(base_retenciones,2))
    output["retenciones"] = str(round(retenciones,2))
    output["base_bajas"] = str(round(base_bajas,2))
    output["bajas"] = str(round(bajas,2))

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

    resultado=enviarPost("CALL uspLiquidarCobranzas( {0},'{1}', {2},{3}\
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

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
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
            # 1. Actualizar el estado de la liquidacion
            liquidacion.ldesembolsada = True
            liquidacion.cxestado = 'P'
            liquidacion.save()

            # 2. grabar el desembolso
            operacion = request.POST.get("cxoperacion")
            forma_pago = request.POST.get("cxformapago")

            if forma_pago =="MOV":
                cuenta_pago = None
            else:
                x = request.POST.get("cxcuentapago")
                cuenta_pago = CuentasEmpresa.objects.filter(pk = x).first()

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

            desembolso = Desembolsos(cxtipooperacion='C'
                , cxoperacion = operacion
                , cxcliente = cliente
                , nvalor = liquidacion.nneto
                , cxformapago = forma_pago
                , cxcuentapago = cuenta_pago
                , cxbeneficiario =id_beneficiario
                , ctbeneficiario = beneficiario
                , cxcuentadestino = cuenta_destino
                , cxusuariocrea = request.user
                , empresa = id_empresa.empresa,
                )
            
            desembolso.save()

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
    resultado=enviarPost("CALL uspRegistroProtesto( {0},'{1}',{2},{3},{4}\
        ,'{5}','{6}',{7},{8},{9},{10}\
        ,'{11}',{12},'{13}','',0)"
        .format(id_cobranza, codigo_cobranza, id_cheque, id_cliente, tipo_factoring
        , forma_cobro, fecha_protesto, valor, valor_nd, motivoprotesto, nusuario
        , tipo_emisor, id_accesorio, tipo_operacion))

    return HttpResponse(resultado)

def GeneraListaProtestosPendientesJSON(request):
    # Es invocado desde la url de una tabla bt

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    documentos = Cheques_protestados.objects\
        .filter(leliminado=False
                , empresa = id_empresa.empresa
                , nsaldocartera__gt = 0).all()

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
    # los datos mostrados deben ser del cliente, no del emisor del cheque.
    output = {}

    if doc.cxtipooperacion=='C':
        cobranza = Documentos_cabecera.objects\
            .filter(cxcheque = doc.cheque).first()
        output["Cobranza"] = cobranza.cxcobranza
    else:
        cobranza = Recuperaciones_cabecera.objects\
            .filter(cxcheque = doc.cheque).first()
        output["Cobranza"] = cobranza.cxrecuperacion

    output['id'] = doc.id
    output["IdCliente"] = cobranza.cxcliente.id
    output["Cliente"] = cobranza.cxcliente.cxcliente.__str__()
    output["IdTipoFactoring"] = cobranza.cxtipofactoring.id
    output["Deposito"] = cobranza.ddeposito.strftime("%Y-%m-%d")
    output["Girador"] = doc.cheque.ctgirador
    output["Cheque"] = doc.cheque.__str__()
    output["IdCobranza"] = cobranza.id
    output["TipoOperacion"] = doc.cxtipooperacion
    output["Protesto"] = doc.dprotesto
    output["Saldo"] = doc.nsaldocartera
    output["Motivo"] = doc.motivoprotesto.ctmotivoprotesto
    

    if doc.notadedebito:
        output["NotaDebito"] = doc.notadedebito.nvalor
    else:
        output["NotaDebito"] = None

    # determinar si cheque fue pagado por comprador 
    if doc.cheque.cxtipoparticipante =='D':
        output["IdComprador"] = doc.cheque.cxparticipante.id
    else:
        output["IdComprador"] = ''
        
    if cobranza.ldepositoencuentaconjunta:
        output["CuentaDeposito"] = 'Cuenta cliente'
    else:
        output["CuentaDeposito"] = cobranza.cxcuentadeposito.__str__()

    return output

def DetalleDocumentosProtesosJSON(request, ids_protestos):
    # filtrar los documentos correspondientes a la lista pasada
    documentos = Documentos_protestados.objects\
        .filter(chequeprotestado__in = ids_protestos.split(',')
                , leliminado = False)
    
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

    # los datos aquí van a obtenerse con el getData de la tb, aunque no se 
    # presenten en el HTML
    output = {}
    output['id'] = doc.id
    output["IdComprador"] = doc.documento.cxcomprador.id
    output["Comprador"] = doc.documento.cxcomprador.cxcomprador.ctnombre
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
    nc=' '; gi=' '; es_cc = False; cd = 'Null'; fd = 'Null'; cc='Null'

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
        cc = deposito["cuenta_conjunta"]
        fd = "'"  + deposito["fecha_deposito"] + "'"

        if  es_cc :
            cd = 'Null'
            if not cc :
                return HttpResponse("Debe especificar la cuenta de depósito")
        else:
            cc = 'Null'
            if not  cd :
                return HttpResponse("Debe especificar la cuenta de depósito")

    if not cuenta_bancaria:
        cuenta_bancaria='Null'
    # Los 2 ultimos parametros son el id de nueva recuperacion y el mensaje de error
    resultado=enviarPost("CALL uspAceptarRecuperacionProtesto( '{0}','{1}','{2}'\
        ,'{3}',{4},'{5}',{6},{7}\
        ,'{8}','{9}',{10},{11}\
        ,{12},{13},'{14}',{15},{16},'',0)"
        .format(id_cliente, tipo_factoring, forma_cobro
        , fecha_cobro, valor_recibido,documentos_cobrados,sobrepago,cuenta_bancaria
        ,nc, gi, cd, fd
        , nusuario,pagador_por_cliente,id_deudor,es_cc,cc))

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

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if request.method =="GET":

        if tipo_operacion=='R':
            lista_cobranzas = Recuperaciones_cabecera.objects\
                .filter(id__in = ids_cobranzas.split(','))
        else:
            lista_cobranzas = Documentos_cabecera.objects\
                .filter(id__in = ids_cobranzas.split(','))

        for c in range(len(lista_cobranzas)):

            cobranza = lista_cobranzas[c]

            if tipo_operacion =='R':
                detalle_cobranza = Recuperaciones_detalle.objects\
                    .filter(recuperacion = cobranza)
            else:
                detalle_cobranza = Documentos_detalle.objects\
                    .filter(cxcobranza = cobranza)

            cuenta_transferencia = Cuenta_transferencia\
                    .objects.cuenta_default(cobranza.cxcliente).first()
            
            datos_operativos = Datos_operativos.objects\
                        .filter(cxcliente = cobranza.cxcliente).first()

            vuelto_cobranza = 0
            # buscar el tipo de factoring
            tipofactoring = cobranza.cxtipofactoring

            for i in range(len(detalle_cobranza)):

                # inicializar
                descuento_cartera=0; descuento_cartera_vencido=0; valor_gao=0
                valor_gaoa=0
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
                    # puede estar cobrando un cheque quitado lo que lo convierte en accesorio
                    accesorios = cobranza.cxformapago == "DEP" or documento_cobrado.accesorioquitado
                    base_bajas=documento_cobrado.nvalorbaja
                    base_retenciones = documento_cobrado.nretenciones

                # documento con tasas. si es accesorio las tasas etan en el accesorio
                if accesorios:
                    if tipo_operacion=='R':
                        documento = documento_cobrado.documentoprotestado.accesorio
                        vuelto = documento_cobrado.nvalorrecuperacion * (100 - documento.nporcentajeanticipo) /100
                    else:
                        if cobranza.cxformapago == "DEP":
                            documento = cobranza.cxaccesorio
                        else:
                            documento = accesorios

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

                # considerar los días condonados
                fechacobrocalculo = cobranza.dcobranza - timedelta(days=documento_cobrado.ndiasacondonar)

                # dias vencidos
                if fechacobrocalculo > documento.dvencimiento:
                    dias_vencidos = fechacobrocalculo - documento.dvencimiento
                    dias_vencidos = dias_vencidos.days

                # generar DC
                dc = Tasas_factoring.objects\
                    .filter(cxtasa='DCAR', empresa = id_empresa.empresa).first()
                
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
                gao = Tasas_factoring.objects\
                    .filter(cxtasa="GAO", empresa = id_empresa.empresa).first()

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
                gaoa = Tasas_factoring.objects\
                    .filter(cxtasa="GAOA", empresa = id_empresa.empresa).first()

                if not gaoa:
                    return HttpResponse("No se ha encontrado tasa de GAOA")

                # aplicar los días de gracia
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
                        # determinar cuantas veces aplicar la tasa según los días de aplicacion
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

                total_otroscargos += ObtenerCargosDeProtestos(cobranza, listaotroscargos)

            # nota:obtener cualkquier cargo cargado a la cobranza
            total_otroscargos += ObtenerOtrosCargosDeCobranza(tipo_operacion
                                                            , cobranza.id
                                                            , codigo_operacion
                                                            , listaotroscargos)

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
        "tipo_factoring" : tipofactoring.id,
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
        "cliente": cobranza.cxcliente.id,
        "cobranzas":json.dumps(listacobranzas),
        "tipo_operacion":tipo_operacion,
        "otros_cargos":json.dumps(listaotroscargos),
    }

    return render(request, template_name, contexto)

def ObtenerCargosDeProtestos(cobranza, listaotroscargos):
    total_cargos = 0

    # Las recueraciones se hacen sobre protestos, determinar los protestos
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
                    , operacion = cobranza_protestada.id
                    , leliminado = False, nsaldo__gt = 0)

            for ndx in nd:

                # el detalle de la nota de debito
                detalle_nd = Notas_debito_detalle.objects\
                    .filter(notadebito = ndx)

                for detallex in detalle_nd:

                    # los cargos indicados en el detalle de la nd
                    cargos = Cargos_detalle.objects\
                        .filter(id = detallex.cargo.id )

                    for cargo in cargos:
                        # verificar que la nd no se encuentre ya registrada, para no duplicar.
                        # eso pasa con recuperaciones del mismo protesto

                        elemento = (GeneraOtroCargoJSONSalida(
                            cargo.id, cargo.cxmovimiento.ctmovimiento
                            , ndx.dnotadebito, cargo.nsaldo, ndx.id
                            , codigo_operacion))

                        try:
                            x = listaotroscargos.index(elemento)
                        except:
                            listaotroscargos.append(elemento)
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

def ReversaLiquidacion(request, pid_liquidacion):
    # # ejecuta un store procedure 
    nusuario = request.user.id
    resultado=enviarPost("CALL uspReversaLiquidarCobranzas( {0},{1},'')"
    .format(pid_liquidacion, nusuario))

    return HttpResponse(resultado)

def ReversaCobranza(request, pid_cobranza, tipo_operacion):
    # ejecuta un store procedure 
    #  EL TIPO DE OPERACION debe determinar el SP a ejecutar: o cobranzas o recuperaciones
    nusuario = request.user.id
    if tipo_operacion=='CC':
        resultado=enviarPost("CALL uspReversarCobranzaCargos( {0},{1},'')"
        .format(pid_cobranza, nusuario))
    elif tipo_operacion[0]=='C':
        resultado=enviarPost("CALL uspReversarCobranzaCartera( {0},{1},'')"
        .format(pid_cobranza, nusuario))
    elif tipo_operacion[0]=='R':
        resultado=enviarPost("CALL uspReversarRecuperacion( {0},{1},'')"
        .format(pid_cobranza, nusuario))
    
    return HttpResponse(resultado)

def GeneraListaCobranzasRegistradasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        cobranzas = Documentos_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                ,'cxcheque', 'cxestado', 'dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
        
        recuperaciones = Recuperaciones_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxrecuperacion'
                ,'cxformacobro'
                ,'nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'R'",''))
    else:

        cobranzas = Documentos_cabecera.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta
                    , empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'C'",''))
                
        recuperaciones = Recuperaciones_cabecera.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta
                    , empresa = id_empresa.empresa)\
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

def GeneraListaLiquidacionesEnNegativoPendientesJSON(request):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    movimiento = Notas_debito_cabecera.objects\
        .filter(cxtipooperacion__in = 'LCRB', leliminado = False
                , nsaldo__gt = 0, empresa = id_empresa.empresa).all()

    docjson = []
    for i in range(len(movimiento)):
        docjson.append(GeneraListaNotasDeDebitoPendientesJSONSalida(movimiento[i])) 

    # docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)
    
def GeneraListaNotasDeDebitoPendientesJSONSalida(transaccion):
    output = {}
    output["id"] = transaccion.id
    output["IdCliente"] = transaccion.cxcliente.id
    output["Cliente"] = transaccion.cxcliente.cxcliente.ctnombre
    output["ND"] = transaccion.cxnotadebito
    output["Fecha"] = transaccion.dnotadebito.strftime("%Y-%m-%d")
    output["Valor"] =  transaccion.nvalor
    output["Saldo"] = transaccion.nsaldo

    # Las ND que vienen de cuentas conjuntas (B) no tienen tipo de factoring
    if transaccion.cxtipooperacion!='B':
        output["IdTipoFactoring"] = transaccion.cxtipofactoring.id
        output["TipoFactoring"] = transaccion.cxtipofactoring.ctabreviacion
    else:
        output["IdTipoFactoring"] = 'NULL'
    
    opx = None
    if transaccion.cxtipooperacion=='L':
        op = Liquidacion_cabecera.objects.filter(pk = transaccion.operacion).first()
        opx = op.cxliquidacion
    if transaccion.cxtipooperacion=='C':
        op = Documentos_cabecera.objects.filter(pk = transaccion.operacion).first()
        opx = op.cxcobranza
    if transaccion.cxtipooperacion=='R':
        op = Recuperaciones_cabecera.objects.filter(pk = transaccion.operacion).first()
        opx = op.cxrecuperacion
    if transaccion.cxtipooperacion=='A':
        op = Ampliaciones_plazo_cabecera.objects.filter(pk = transaccion.operacion).first()
        opx = op.dampliacionhasta
    
    output["Operacion"] = opx

    return output

def DetalleNotasDebitoPendientesJSON(request, ids_documentos):
    # filtrar los documentos correspondientes a la lista pasada
    documentos = Notas_debito_cabecera.objects\
        .filter(id__in = ids_documentos.split(','), leliminado = False)
    
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(documentos)):
        tempBlogs.append(DetalleNotasDebitoPendientesJSONSalida(documentos[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DetalleNotasDebitoPendientesJSONSalida(doc):
    # con los datos numericos entre comillas si se calcula el total
    # de la columna en la tabla. Del otro tipo, no

    # los datos aquí van a obtenerse con el getData de la tb, aunque no se 
    # presenten en el HTML
    output = {}
    output['id'] = doc.id
    output["ND"] = doc.cxnotadebito
    output["Emision"] = doc.dnotadebito.strftime("%Y-%m-%d")
    output["SaldoActual"] = doc.nsaldo
    output["Cobro"] = doc.nsaldo
    output["SaldoFinal"] = "0.0"
    opx = None
    if doc.cxtipooperacion=='L':
        op = Liquidacion_cabecera.objects.filter(pk = doc.operacion).first()
        opx = op.cxliquidacion
    if doc.cxtipooperacion=='C':
        op = Documentos_cabecera.objects.filter(pk = doc.operacion).first()
        opx = op.cxcobranza
    if doc.cxtipooperacion=='R':
        op = Recuperaciones_cabecera.objects.filter(pk = doc.operacion).first()
        opx = op.cxrecuperacion
    if doc.cxtipooperacion=='A':
        op = Ampliaciones_plazo_cabecera.objects.filter(pk = doc.operacion).first()
        opx = op.dampliacionhasta
    
    output["Operacion"] = opx

    return output

def DatosCobroNotaDebito(request, id, sdo, cobro):
    template_name = "cobranzas/datoscobronotadebito_modal.html"
    contexto={
        "id": id,
        "saldo" : sdo,
        "valor_cobrado": cobro,
    }
    return render(request, template_name, contexto)

def AceptarCobranzaNotasDebito(request):
    # ejecuta un store procedure 
    # Devuelve el control a un proceso js
    resultado = 'OK'
    nc=' '; gi=' ';  cd = 0; fd = 'Null'

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
        fd = "'"  + deposito["fecha_deposito"] + "'"

        if not cd :
            return HttpResponse("Debe especificar la cuenta de depósito")

    if not cuenta_bancaria:
        cuenta_bancaria='Null'
    
    # # para los debitos de cuentas conjuntas que se registran sin cobranza
    # # no hay tipo de factoring, se carga con NULL 
    # if tipo_factoring != 'NULL':
    #     tipo_factoring="'" + tipo_factoring + "'"

    # Los 2 ultimos parametros son el id de cheque accesorio y el mensaje de error
    resultado=enviarPost("CALL uspAceptarCobranzaCargos({0},{1},'{2}','{3}',{4}\
        ,{5},{6}\
        ,'{7}','{8}',{9},{10}\
        ,'{11}', {12},Null,0)"
        .format(id_cliente, tipo_factoring, forma_cobro, fecha_cobro, valor_recibido
        ,sobrepago,cuenta_bancaria
        ,nc,gi, cd, fd
        ,documentos_cobrados, nusuario))

    return HttpResponse(resultado)

def GeneraListaLiquidacionesRegistradasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        movimiento = Liquidacion_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddesembolso'
                ,'cxtipofactoring__ctabreviacion','cxliquidacion'
                ,'ctinstrucciondepago', 'cxtipooperacion'
                ,'nneto', 'dliquidacion','ldesembolsada'
                ,'dregistro', 'leliminado', 'cxestado'
                , 'id')
    else:

        movimiento = Liquidacion_cabecera.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta
                    ,empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddesembolso'
                ,'cxtipofactoring__ctabreviacion','cxliquidacion'
                ,'ctinstrucciondepago', 'cxtipooperacion'
                ,'nneto', 'dliquidacion','ldesembolsada'
                ,'dregistro', 'leliminado', 'cxestado'
                , 'id')
          
    tempBlogs = []
    for i in range(len(movimiento)):
        tempBlogs.append(GeneraListaLiquidacionesJSONSalida(movimiento[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaLiquidacionesJSONSalida(transaccion):
    output = {}
    output['id'] = transaccion['id']
    output["Cliente"] = transaccion['cxcliente__cxcliente__ctnombre']
    output["Operacion"] = transaccion['cxliquidacion']
    output["Fecha"] = transaccion['dliquidacion'].strftime("%Y-%m-%d")
    output["Estado"] = transaccion['cxestado']
    output["Valor"] =  transaccion['nneto']
    output["TipoFactoring"] = transaccion['cxtipofactoring__ctabreviacion']
    output["Registro"] = transaccion["dregistro"]

    output["TipoOperacion"] = transaccion["cxtipooperacion"]

    return output

def GeneraListaCobranzasCargosRegistradasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        movimiento = Cargos_cabecera.objects\
            .filter(empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago'
                ,'nvalor', 'dcobranza'
                ,'cxcheque', 'cxestado', 'dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'CC'",''))
    else:

        movimiento = Cargos_cabecera.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta
                    , empresa = id_empresa.empresa)\
                .values('cxcliente__cxcliente__ctnombre','ddeposito'
                ,'cxtipofactoring__ctabreviacion','cxcobranza'
                ,'cxformapago','nvalor', 'dcobranza'
                , 'cxcheque', 'cxestado','dregistro'
                , 'id', 'cxcuentatransferencia','nsobrepago')\
                    .annotate(tipo=RawSQL("select 'CC'",''))
                

    tempBlogs = []
    for i in range(len(movimiento)):
        tempBlogs.append(GeneraListaCobranzasCargosJSONSalida(movimiento[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaCobranzasCargosJSONSalida(transaccion):
    output = {}
    output['id'] = transaccion['id']
    output["Cliente"] = transaccion['cxcliente__cxcliente__ctnombre']
    output["Operacion"] = transaccion['cxcobranza']
    output["Fecha"] = transaccion['dcobranza'].strftime("%Y-%m-%d")
    output["Estado"] = transaccion['cxestado']
    output["Valor"] =  transaccion['nvalor']
    output["TipoFactoring"] = transaccion['cxtipofactoring__ctabreviacion']
    output["Registro"] = transaccion["dregistro"]

    # if 'protestada' in transaccion['tipo']:
    #     output["Detalle"] = transaccion['cxformapago']
    # else:
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

    # se necesita el tipo de operacion para saber que va a imprimir o reversar
    output["TipoOperacion"] = transaccion["tipo"]
    # output["FormaPago"] = transaccion["cxformapago"]

    return output

def ObtenerOtrosCargosDeCobranza(tipo_operacion, cobranza, codigo_operacion\
        , listaotroscargos):
    total_cargos = 0

    # la nd se registra sobre la recuperacion o cobranza protestada
    nd = Notas_debito_cabecera.objects\
        .filter(cxtipooperacion = tipo_operacion, operacion = cobranza)

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
                    , ndx.dnotadebito, cargo.nsaldo, ndx.id
                    , codigo_operacion))

                total_cargos += cargo.nsaldo

    return total_cargos

def ReversaProtesto(request, id_cobranza,tipo_operacion,id_protesto, cobranza
                    , cliente_id, factoring_id):
    # # ejecuta un store procedure 
    nusuario = request.user.id
    resultado=enviarPost("CALL uspReversaProtesto( '{0}',{1},{2},'{3}','{4}'\
        ,'{5}',{6},'')"
    .format(tipo_operacion,id_cobranza,id_protesto, cobranza,cliente_id
        ,factoring_id, nusuario))

    return HttpResponse(resultado)

def CanjeDeCheque(request, cheque_id, cliente_id, deudor_id):
    template_path = 'cobranzas/datoscanjecheque_modal.html'

    cliente = Datos_generales.objects.filter(pk = cliente_id).first()
    comprador = Datos_compradores.objects.filter(pk = deudor_id).first()

    cuentas = Cuentas_bancarias\
        .objects.filter(cxparticipante = cliente.cxcliente.id \
            , leliminado = False, lpropia = True\
            , cxtipocuenta = 'C').all()
    cuentas_deudor = Cuentas_bancarias\
        .objects.filter(cxparticipante = comprador.cxcomprador.id \
            , leliminado = False, lpropia = True\
            , cxtipocuenta = 'C').all()

    context={
        'cheque':cheque_id,
        'form_cheque': AccesoriosForm,
        "cuentas_bancarias_cliente" : cuentas,
        "cuentas_bancarias_deudor" : cuentas_deudor,
        'cliente_id':cliente_id,
        'deudor_id':deudor_id,
        }
    
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    if request.method =='POST':

        with transaction.atomic():
            # marcar el cheque como canjeado
            cheque = ChequesAccesorios.objects.filter(id = cheque_id).first()

            cheque.lcanjeado = True
            cheque.save()

            # crear nuevo cheque
            propietario  = request.POST.get('cxpropietariocuenta')
            numero_cheque  = request.POST.get('ctcheque')
            girador  = request.POST.get('ctgirador')

            if propietario=='C':
                cuenta_banco = request.POST.get('cuenta_cliente')
            else:
                cuenta_banco = request.POST.get('cuenta_deudor')

            cuenta = Cuentas_bancarias.objects.filter(pk = cuenta_banco).first()
            bco_id = cuenta.cxbanco
            cta_id = cuenta.cxcuenta
            
            nuevo_cheque = ChequesAccesorios(
                cxpropietariocuenta = propietario,
                cxbanco = bco_id,
                ctcuenta = cta_id,
                ctcheque = numero_cheque,
                ctgirador = girador,
                documento = cheque.documento,
                ntotal = cheque.ntotal,
                dvencimiento = cheque.dvencimiento,
                nporcentajeanticipo = cheque.nporcentajeanticipo,
                ntasacomision = cheque.ntasacomision,
                ntasadescuento = cheque.ntasadescuento,
                nanticipo = cheque.nanticipo,
                ngao = cheque.ngao,
                ndescuentocartera = cheque.ndescuentocartera,
                nplazo = cheque.nplazo,
                cxestado = cheque.cxestado,
                ncanjeadopor = cheque.id,
                ndiasprorroga = cheque.ndiasprorroga,
                ncontadorprorrogas = cheque.ncontadorprorrogas,
                dultimageneraciondecargos = cheque.dultimageneraciondecargos,
                cxusuariocrea = request.user,            
                empresa = id_empresa.empresa,
            )
            if nuevo_cheque:
                nuevo_cheque.save()

            # registrar canje con el motivo
            motivo  = request.POST.get('motivo')

            canje = Cheques_canjeados(
                cxcliente = cliente,
                accesoriooriginal = cheque,
                accesorionuevo = nuevo_cheque,
                ctmotivocanje = motivo,
                cxusuariocrea = request.user,            
                empresa = id_empresa.empresa,
            )
            if canje:
                canje.save()

        return redirect("cobranzas:listachequesadepositar")

    return render(request, template_path, context)

def QuitarAccesorio(request, cheque_id, cliente_ruc):
    template_path = 'cobranzas/datosquitaraccesorio_modal.html'

    context={
        'cheque':cheque_id,
        'cliente_ruc':cliente_ruc,
        }
    
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    if request.method =='POST':
        with transaction.atomic():

            cheque = ChequesAccesorios.objects.filter(id = cheque_id).first()

            # registrar quitada con el motivo
            motivo  = request.POST.get('motivo')
            cliente = Datos_generales.objects.filter(cxcliente = cliente_ruc).first()
            
            quitado = Cheques_quitados(
                cxcliente = cliente,
                nsaldo = cheque.ntotal,
                ctmotivoquitado = motivo,
                cxusuariocrea = request.user,
                empresa = id_empresa.empresa,
            )
            if quitado:
                quitado.save()


            cheque.laccesorioquitado = True
            cheque.chequequitado = quitado
            cheque.save()

        return redirect("cobranzas:listachequesadepositar")

    return render(request, template_path, context)

def AmpliacionDePlazo(request, ids, tipo_factoring, tipo_asignacion, id_cliente):
    template_path = 'cobranzas/datosampliacionplazo_form.html'
    carga_dc = "No"
    acumula_gao='No'
    iva_gaoa = 'No'
    iva_dc = 'No'

    # buscar en la configuracion del tipo de factoring las condiciones para menajer 
    # las ampliaciones de plazo

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # buscar el tipo de factoring
    tipo_factoring = Tipos_factoring.objects.get(id=tipo_factoring)

    if not tipo_factoring:
        return HttpResponse("Tipo de factoring no existe:" + tipo_factoring)
    if tipo_factoring.lcargadcenampliacionplazo:
        carga_dc="Si"
    if tipo_factoring.lacumulagaoaatasagao:
        acumula_gao="Si"

    # datos de tasa gaoa/dc
    gaoa = Tasas_factoring.objects\
        .filter(cxtasa="GAOA", empresa = id_empresa.empresa).first()
    
    if not gaoa:
        return HttpResponse("no encontró tasa de gaoa")
    
    if gaoa.lcargaiva: iva_gaoa = 'Si'

    dc = Tasas_factoring.objects\
        .filter(cxtasa="DCAR", empresa = id_empresa.empresa).first()
    
    if not dc:
        return HttpResponse("no encontró tasa de descuento de cartera")
    
    if dc.lcargaiva: iva_dc='Si'

    dic_gaoa  = {'carga_iva': iva_gaoa
        , 'descripcion': gaoa.ctdescripcionenreporte
        , 'acumula_gao': acumula_gao
        , 'iniciales': gaoa.ctinicialesentablas}

    dic_dc = {'carga_iva': iva_dc
        , 'descripcion': dc.ctdescripcionenreporte
        , 'generar':carga_dc
        , 'iniciales': dc.ctinicialesentablas}

    cliente = Datos_generales.objects.filter(pk = id_cliente).first()
    context={
        'ids':ids,
        'tipo_asignacion':tipo_asignacion,
        'gaoa': dic_gaoa,
        'dc' : dic_dc,
        'porcentaje_iva':12,
        'id_cliente': id_cliente, 
        'cliente': cliente.cxcliente.ctnombre,
        'tipo_factoring': tipo_factoring.id
        }
    return render(request, template_path, context)

from django.utils.dateparse import parse_date

def DetalleCargosAmpliacionPlazo(request, ids, tipo_asignacion, fecha_corte
                                 , carga_dc, acumula_gao, id_cliente):
    # GRABA EN LA TABLA DE DOCUMENTOS LAS TASAS Y CARGOS POR AMPLIACION
    # inicializar variables
    tasa_gaoa = 0
    dc=None
    arr_acc = []    # estos dos arreglos son
    arr_fac = []    # usados para separar facturas de accesorio quitados

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # obtener las tasas de los datos operativos del ciente
    datos_operativos = Datos_operativos.objects\
                .filter(cxcliente = id_cliente).first()
    if not datos_operativos:
        return HttpResponse("no encontró registro de datos operativos")
    
    tasa_gaoa = datos_operativos.ntasagaoa

    # datos de tasa gao/dc
    gaoa = Tasas_factoring.objects\
        .filter(cxtasa="GAOA", empresa = id_empresa.empresa).first()
    if not gaoa:
        return HttpResponse("no encontró registro de tasa de gao en tabla de tasas de factoring")

    if carga_dc=='Si':
        dc = Tasas_factoring.objects\
            .filter(cxtasa="DCAR", empresa = id_empresa.empresa).first()
        if not dc:
            return HttpResponse("no encontró registro de tasa de descuento de catera en tabla de tasas de factoring")

    fecha_corte = parse_date(fecha_corte)

    # recuperar los documentos
    # si es Factura pura podría ser un accesorio quitado

    if tipo_asignacion == FACTURAS_PURAS:

        ids = ids.split(',')

        for id in ids:
            if int(id) < 0:
                arr_acc.append(-int(id))
            else:
                arr_fac.append(id)

        documentos = Documentos.objects.filter(id__in=arr_fac)
    else:
       documentos = ChequesAccesorios.objects.filter(id__in = ids.split(','))
            
    # calcular cargos
    for i in range(len(documentos)):
        CalcularCargosPorDocumento(documentos[i], gaoa ,dc, fecha_corte
                                    , tasa_gaoa, acumula_gao)
        
    if arr_acc:
        quitados = ChequesAccesorios.objects.filter(id__in = arr_acc)
        for i in range(len(quitados)):
            CalcularCargosPorDocumento(quitados[i], gaoa ,dc, fecha_corte
                                        , tasa_gaoa, acumula_gao)
    
    return HttpResponse("OK")

def CalcularCargosPorDocumento(doc, gaoa, dc, fecha_hasta, tasa_gaoa, acumula_gao
                               , tasa_dc = None):
    # el último parametro va cuando se trata de edicion de tasas

    if doc.dultimageneraciondecargos:
        plazo =fecha_hasta- doc.dultimageneraciondecargos 
    else:
        plazo = fecha_hasta - doc.dvencimiento
    
    plazo = plazo.days

    if plazo < 0 : plazo = 0

    doc.nplazoap = plazo  

    if acumula_gao == 'Si':
        tasa_gaoa += doc.ntasacomision

    doc.ntasacomisionap = tasa_gaoa

    # gaoa
    if gaoa.lsobreanticipo:
        doc.ngaoaap = (doc.ntotal * doc.nporcentajeanticipo 
                       * doc.ntasacomisionap / 10000)
    else:
        doc.ngaoaap = (doc.ntotal * doc.ntasacomisionap / 100)

    if gaoa.lflat :
        # determinar cuantas veces aplicar la tasa según los días de aplicacion
        x = math.ceil(plazo/gaoa.ndiasperiocidad)
        doc.ngaoaap = doc.ngaoaap * x
    else:
        doc.ngaoaap = (doc.ngaoaap * plazo / gaoa.ndiasperiocidad)

    # dc
    if dc:
        if tasa_dc == None:
            doc.ntasadescuentoap = doc.ntasadescuento
        else:
            doc.ntasadescuentoap = tasa_dc
            
        if dc.lsobreanticipo:
            doc.ndescuentocarteraap = (doc.ntotal * doc.nporcentajeanticipo * doc.ntasadescuentoap / 10000)
        else:
            doc.ndescuentocarteraap = (doc.ntotal * doc.ntasadescuentoap / 100)

        if not dc.lflat:
            doc.ndescuentocarteraap = (doc.ndescuentocarteraap * plazo / dc.ndiasperiocidad)
    else:
        doc.ntasadescuentoap = 0
        doc.ndescuentocarteraap = 0

    doc.save()

def GeneraDetalleCargosAmpliacionPlazoJSON(request, ids, tipo_asignacion):
    # Es invocado desde la url
    # crear detalle de salida para el contexto
    # no calcula, ni graba cargos, recupera los documentos
    arr_acc = []    # estos dos arreglos son
    arr_fac = []    # usados para separar facturas de accesorio quitados

    if tipo_asignacion==FACTURAS_PURAS:
        ids = ids.split(',')

        for id in ids:
            if int(id) < 0:
                arr_acc.append(-int(id))
            else:
                arr_fac.append(id)

        documentos = Documentos.objects.filter(id__in=arr_fac)
    else:
        documentos = ChequesAccesorios.objects\
            .filter(id__in=ids.split(','), leliminado = False)

    tempBlogs = []
    for i in range(len(documentos)):
        tempBlogs.append(GeneraDetalleCargosAmpliacionPlazoOutput(documentos[i]
                                                                  ,tipo_asignacion )) 
    if arr_acc:
        quitados = ChequesAccesorios.objects.filter(id__in = arr_acc)
        for i in range(len(quitados)):
            tempBlogs.append(GeneraDetalleCargosAmpliacionPlazoOutput(quitados[i]
                                                                  ,'A' )) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    
    return JsonResponse( data)

def GeneraDetalleCargosAmpliacionPlazoOutput(doc, tipo_asignacion):
    output = {}

    # el id debe ser del documento o el accesorio, para poder editar las tasas
    output['id'] = doc.id
    output["Tipo_documento"] = tipo_asignacion
  
    # los siguientes 3 campos pertenecen al documento y no se encuentran en los cheques
    if tipo_asignacion==FACTURAS_PURAS:
        output["Asignacion"] = doc.cxasignacion.cxasignacion
        output["id_asignacion"] = doc.cxasignacion.id
        output["Documento"] = doc.ctdocumento
        output["id_documento"] = doc.id
        output["id_documento_accesorio"] = doc.id
        output["Saldo"] = doc.nsaldo
    else:
        output["Asignacion"] = doc.documento.cxasignacion.cxasignacion
        output["id_asignacion"] = doc.documento.cxasignacion.id
        output["Documento"] = doc.documento.ctdocumento
        output["id_documento"] = doc.documento.id
        output["id_documento_accesorio"] = doc.id
        output["Saldo"] = doc.ntotal
    
    if doc.dultimageneraciondecargos:
        output["UltimaGeneracioncargos"] = doc.dultimageneraciondecargos
    else:
        output["UltimaGeneracioncargos"] = doc.dvencimiento

    output["Plazo"] = doc.nplazoap
    output["Tasa_GAOA"] = round( doc.ntasacomisionap,2)
    output["Valor_GAOA"] = doc.ngaoaap
    output["Tasa_DC"] = round(doc.ntasadescuentoap,2)
    output["Valor_DC"] = doc.ndescuentocarteraap

    return output

def SumaCargos(request,ids, tipo_asignacion, gaoa_carga_iva, dc_carga_iva
               , porcentaje_iva=12):
    # lee los datos de la tabla solicutid documentos
    arr_acc = []    # estos dos arreglos son
    arr_fac = []    # usados para separar facturas de accesorio quitados

    g=Decimal(0); d=Decimal(0); 
    iva=0.0; total=0.0

    if tipo_asignacion==FACTURAS_PURAS:
        ids = ids.split(',')

        for id in ids:
            if int(id) < 0:
                arr_acc.append(-int(id))
            else:
                arr_fac.append(id)

        documentos = Documentos.objects.filter(id__in=arr_fac)\
            .values('ngaoaap', 'ndescuentocarteraap')
        quitados = ChequesAccesorios.objects.filter(id__in = arr_acc)\
            .values('ngaoaap', 'ndescuentocarteraap')
    else:
        documentos = ChequesAccesorios.objects\
            .filter(id__in=ids.split(','),leliminado = False)

    # gaoa
    total_gaoa = documentos.aggregate(suma_gaoa = Sum('ngaoaap'))
    
    g = total_gaoa["suma_gaoa"]
    
    if arr_acc:
        if not g: g = 0

        total_gaoa = quitados.aggregate(suma_gaoa = Sum('ngaoaap'))
        g += total_gaoa["suma_gaoa"]

    # dc
    total_dc = documentos.aggregate(suma_dc = Sum('ndescuentocarteraap'))
    d = total_dc["suma_dc"]

    if arr_acc:
        if not d: d = 0

        total_dc = quitados.aggregate(suma_dc = Sum('ndescuentocarteraap'))
        d += total_dc["suma_dc"]

    # iva
    base = 0
    if gaoa_carga_iva=="Si":
        base += g
    if dc_carga_iva=="Si":
        base += d
    iva = round( base * porcentaje_iva / 100,2)
    # redondear a 2 decimales?
    # neto
    total =   g + d + iva

    data={'gaoa':str(g)
        , 'dc':str(d)
        , 'iva': str(iva)
        , 'total':str(total)}
    
    return HttpResponse(json.dumps(data), content_type = "application/json")

def Prorroga(request, id, tipo_asignacion, vencimiento, numero_factura):
    template_path = 'cobranzas/datosdiasprorroga_modal.html'

    if tipo_asignacion =='F':
        documento = Documentos.objects.filter(pk=id).first()
    else:
        documento = ChequesAccesorios.objects.filter(pk=id).first()

    context={
        'id':id,
        'tipo_asignacion':tipo_asignacion,
        'vencimiento': vencimiento,
        'numero_factura' : numero_factura, 
        'cantidad_prorrogas' : documento.ncontadorprorrogas,
        'dias':0,
        }
    
    if request.method =="POST":

        dias = request.POST.get("dias_id")
        dias = Decimal(dias)
        
        if documento:
            documento.ndiasprorroga += dias
            documento.ncontadorprorrogas += 1
            documento.save()
        else:
            return "docuemnto no encontrada"

        if tipo_asignacion==FACTURAS_PURAS:
            return redirect("cobranzas:listadocumentosvencidos",)
        else:
            return redirect("cobranzas:listachequesadepositar",)

    return render(request, template_path, context)

from operaciones.forms import TasasAPAccesoriosForm, TasasAPDocumentoForm

def EditarTasasDocumentoAmpliacionDePlazo(request, documento_id, fecha_ampliacion
                                          , tipo_asignacion):
    template_name = "cobranzas/datoscambiotasasampliaciondeplazo_modal.html"
    contexto={}
    numero_documento=""
    formulario = {}
    # si son facturas puras los documentos son las facturas
    # si son accesorios los documentos son los cheques

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if tipo_asignacion ==FACTURAS_PURAS:
        documento = Documentos.objects.filter(pk=documento_id).first()
        es_facturas_puras = True
        e = {'ntasacomisionap': documento.ntasacomisionap
             , 'ntasadescuentoap': documento.ntasadescuentoap}
        formulario = TasasAPDocumentoForm(e)
    else:
        documento = ChequesAccesorios.objects.filter(pk=documento_id).first()
        es_facturas_puras = False
        e = {'ntasacomisionap': documento.ntasacomisionap
             , 'ntasadescuentoap': documento.ntasadescuentoap}
        formulario = TasasAPAccesoriosForm(e)

    if request.method=='GET':
        if documento:
            if es_facturas_puras:
                numero_documento=documento.ctdocumento
            else:
                numero_documento=documento.documento.ctdocumento

    contexto={ 'documento_id':documento_id
        , 'documento':numero_documento
        , 'fecha_ampliacion': fecha_ampliacion
        , 'tipo_asignacion': tipo_asignacion 
        , 'tasa_gaoa': documento.ntasacomisionap
        , 'tasa_dc': documento.ntasadescuentoap
        , 'form' :formulario
        }

    if request.method=='POST':
        ntasacomision = request.POST.get("ntasacomisionap")
        ntasadescuentocartera = request.POST.get("ntasadescuentoap")

        ntasacomision = Decimal(ntasacomision)
        ntasadescuentocartera = Decimal(ntasadescuentocartera)
        
        # calcular y grabar los valores para cada tasa y grabarlos en el registro del documento
        # datos de tasa gao/dc
        gaoa = Tasas_factoring.objects\
            .filter(cxtasa="GAOA", empresa = id_empresa.empresa).first()
        
        dc = Tasas_factoring.objects\
            .filter(cxtasa="DCAR", empresa = id_empresa.empresa).first()
        
        fecha_ampliacion = parse_date(fecha_ampliacion)
            
        # cuando edita no necesita enviar clase de cliente ni codigo de condicion operativa
        # si necesita el tipo de asignacion para saber donde grbar las tasas

        CalcularCargosPorDocumento(documento, gaoa ,dc, fecha_ampliacion
                                    , ntasacomision, 'No', ntasadescuentocartera)
        return HttpResponse(1)

    return render(request, template_name, contexto)

def AceptarAmpliacionDePlazo(request):
    # ejecuta un store procedure 

    objeto=json.loads(request.body.decode("utf-8"))

    id_cliente=objeto["id_cliente"]
    fecha_emision=objeto["emision_nd"]
    fecha_ampliacion=objeto["fecha_corte"]
    id_factoring=objeto["tipo_factoring"]
    pngao=objeto["ngao"]
    pndescuentocartera=objeto["ndescuentocartera"]
    pniva=objeto["niva"]
    valor=objeto["valor_ampliacion"]
    porcentaje_iva=objeto["porcentaje_iva"]
    documentos=objeto["arr_documentos_ampliados"]
    nusuario = request.user.id

    resultado=enviarPost("CALL uspAmpliacionDePlazo( {0},{1}, '{2}'\
        ,'{3}',{4},{5}, {6}\
        ,{7},{8},{9},'{10}','',0)"
        .format(id_cliente, id_factoring, fecha_emision
                , fecha_ampliacion, valor, pngao, pndescuentocartera
                , porcentaje_iva, pniva, nusuario, documentos))

    return HttpResponse(resultado)

def GeneraListaAmpliacionesPendientesJSON(request):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    movimiento = Notas_debito_cabecera.objects\
        .filter(cxtipooperacion = 'A', leliminado = False
                , nsaldo__gt = 0, empresa = id_empresa.empresa).all()

    docjson = []
    for i in range(len(movimiento)):
        docjson.append(GeneraListaNotasDeDebitoPendientesJSONSalida(movimiento[i])) 

    # docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)
