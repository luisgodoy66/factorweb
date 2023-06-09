from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q, FilteredRelation, F
from django.db.models.expressions import RawSQL 
from django.http import JsonResponse
from django.db import transaction
import time
import os

from .models import Plan_cuentas, Cuentas_especiales, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring, Factura_venta\
    , Items_facturaventa, Impuestos_facturaventa, Diario_cabecera, Transaccion
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from empresa.models import Cuentas_bancarias, Tipos_factoring, Tasas_factoring\
    , Puntos_emision, Contador
from operaciones.models import Asignacion as Operacion
from cobranzas.models import Liquidacion_cabecera
from operaciones.models import Ampliaciones_plazo_cabecera, Desembolsos
from clientes.models import Datos_generales

from .forms import CuentasEspecialesForm, CuentasBancosForm, FacturaVentaForm\
    , CuentasTiposFactoringForm, CuentasTasaTiposFactoringForm

import xml.etree.cElementTree as etree
from decimal import Decimal

from .sri import _get_detail_element, _get_invoice_element, _get_tax_element, calculate_check_digit

class CuentasView(LoginRequiredMixin, generic.ListView):
    model = Plan_cuentas
    template_name = "contabilidad/listacuentascontables.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Plan_cuentas.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa)\
            .order_by('cxcuenta')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(CuentasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasEspecialesNew(LoginRequiredMixin, generic.CreateView):
    model = Cuentas_especiales
    template_name = "contabilidad/datoscuentasespeciales_form.html"
    context_object_name='cuentas'
    form_class = CuentasEspecialesForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CuentasEspecialesNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P',leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasEspecialesNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentasEspecialesEdit(LoginRequiredMixin, generic.UpdateView):
    model = Cuentas_especiales
    template_name='contabilidad/datoscuentasespeciales_form.html'
    context_object_name='cuentas'
    form_class = CuentasEspecialesForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # pk = self.kwargs.get('pk')

        context = super(CuentasEspecialesEdit, self).get_context_data(**kwargs)
        # context["id"]=pk
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasEspecialesEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs
    
class CuentasBancosView(LoginRequiredMixin, generic.ListView):
    model = Cuentas_bancarias
    template_name = "contabilidad/listacuentasbancos.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Cuentas_bancarias.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context = super(CuentasBancosView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentaBancoNew(LoginRequiredMixin, generic.CreateView):
    model=Cuentas_bancos
    template_name="contabilidad/datoscuentabanco_modal.html"
    context_object_name = "consulta"
    form_class=CuentasBancosForm
    success_url=reverse_lazy("contabilidad:listacuentasbancos")
    success_message="cuenta creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        banco_id = self.kwargs.get('banco_id')
        nombre_banco = self.kwargs.get('banco')
        context = super(CuentaBancoNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["banco"] = nombre_banco
        context["banco_id"] = banco_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaBancoNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentaBancoEdit(LoginRequiredMixin, generic.UpdateView):
    model=Cuentas_bancos
    template_name="contabilidad/datoscuentabanco_modal.html"
    context_object_name = "consulta"
    form_class=CuentasBancosForm
    success_url=reverse_lazy("contabilidad:listacuentasbancos")
    success_message="cuenta modificada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        banco_id = self.kwargs.get('banco_id')
        nombre_banco = self.kwargs.get('banco')
        context = super(CuentaBancoEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["banco"] = nombre_banco
        context["banco_id"] = banco_id
        context["pk"] = id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaBancoEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentasTiposFactoringView(LoginRequiredMixin, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tipos_factoring.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context = super(CuentasTiposFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentaTipoFactoringNew(LoginRequiredMixin, generic.CreateView):
    model=Cuentas_tiposfactoring
    template_name="contabilidad/datoscuentatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTiposFactoringForm
    success_url=reverse_lazy("contabilidad:listacuentastiposfactoring")
    success_message="cuenta creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        tipofactoring_id = self.kwargs.get('tipofactoring_id')
        nombre_tipofactoring = self.kwargs.get('tipofactoring')
        context = super(CuentaTipoFactoringNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaTipoFactoringNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentaTipoFactoringEdit(LoginRequiredMixin, generic.UpdateView):
    model=Cuentas_tiposfactoring
    template_name="contabilidad/datoscuentatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTiposFactoringForm
    success_url=reverse_lazy("contabilidad:listacuentastiposfactoring")
    success_message="cuenta modificada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        tipofactoring_id = self.kwargs.get('tipofactoring_id')
        nombre_tipofactoring = self.kwargs.get('tipofactoring')
        context = super(CuentaTipoFactoringEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        context["pk"] = id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaTipoFactoringEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentasTasasFactoringView(LoginRequiredMixin, generic.ListView):
    model = Tasas_factoring
    template_name = "contabilidad/listacuentastasasfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tasas_factoring.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context = super(CuentasTasasFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasTasaTiposFactoringView(LoginRequiredMixin, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastasatiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        id_tasa = self.kwargs.get('tasa')
        # qs= Tipos_factoring.objects\
        #     .annotate(registros = FilteredRelation('cuenta_tasatipofactoring'
        #                                            ,condition = Q(cuenta_tasatipofactoring__tasafactoring__id=id_tasa) ))\
        #     .values('id','cttipofactoring'
        #             ,'cuenta_tasatipofactoring__cuenta__ctcuenta'
        #             , 'cuenta_tasatipofactoring__tasafactoring__id'
        #             , 'cuenta_tasatipofactoring__id')\
        #     .filter(leliminado = False, empresa = id_empresa.empresa, registros__isnull = True)
        # en este query la condition ingresada en el FilterdRelation no se pasa al query
        # y no se filtra por la tasa ingresada. La filtración se está resolviendo en la
        # forma más burda en el HTML con condiciones tags de Django.
        qs=Tipos_factoring.objects\
            .filter(empresa=id_empresa.empresa
                    , cuenta_tasatipofactoring__tasafactoring = id_tasa)\
            .values('id', 'cttipofactoring'
                    ,'cuenta_tasatipofactoring__cuenta__ctcuenta'
                    ,'cuenta_tasatipofactoring'
                    ,'cuenta_tasatipofactoring__tasafactoring')
        
        qs2=Tipos_factoring.objects\
            .annotate(registros=FilteredRelation('cuenta_tasatipofactoring'
                                                 , condition = Q(cuenta_tasatipofactoring__tasafactoring=id_tasa)))\
            .values('id','cttipofactoring'
                    , 'registros__cuenta__ctcuenta'
                    ,'cuenta_tasatipofactoring'
                    ,'cuenta_tasatipofactoring__tasafactoring')\
            .filter(empresa = id_empresa.empresa, registros__cuenta__ctcuenta__isnull=True)
        return qs.union(qs2)

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        id_tasa = self.kwargs.get('tasa')
        nombre_tasa = self.kwargs.get('nombre_tasa')
        context = super(CuentasTasaTiposFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp
        context["id_tasa"]=id_tasa
        context["nombre_tasa"]=nombre_tasa

        return context
    
class CuentaTasaTipoFactoringNew(LoginRequiredMixin, generic.CreateView):
    model=Cuentas_tasasfactoring
    template_name="contabilidad/datoscuentatasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTasaTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        tipofactoring_id = self.kwargs.get('tipofactoring_id')
        nombre_tipofactoring = self.kwargs.get('tipofactoring')
        context = super(CuentaTasaTipoFactoringNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["tasafactoring"] = nombre_tasafactoring
        context["tasafactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaTasaTipoFactoringNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        return reverse_lazy("contabilidad:listacuentastasatiposfactoring"
            , kwargs={'tasa': tasafactoring_id, 'nombre_tasa':nombre_tasafactoring})

class CuentaTasaTipoFactoringEdit(LoginRequiredMixin, generic.UpdateView):
    model=Cuentas_tasasfactoring
    template_name="contabilidad/datoscuentatasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTasaTiposFactoringForm
    success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta modificada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        tipofactoring_id = self.kwargs.get('tipofactoring_id')
        nombre_tipofactoring = self.kwargs.get('tipofactoring')
        context = super(CuentaTasaTipoFactoringEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["tasafactoring"] = nombre_tasafactoring
        context["tasafactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        context["pk"] = id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaTasaTipoFactoringEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        return reverse_lazy("contabilidad:listacuentastasatiposfactoring"
            , kwargs={'tasa': tasafactoring_id, 'nombre_tasa':nombre_tasafactoring})

class PendientesGenerarFacturaView(LoginRequiredMixin, generic.ListView):
    model = Plan_cuentas
    template_name = "contabilidad/listapendientesgenerarfactura.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        asgn=Operacion.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False, )\
            .values('cxcliente__cxcliente__ctnombre', 'cxasignacion', 'ddesembolso', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Asignación'",'')
                      , tipo = RawSQL("select 'LA'",''))\
            .order_by('dregistro')
        
        cobr=Liquidacion_cabecera.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False)\
            .values('cxcliente__cxcliente__ctnombre', 'cxliquidacion', 'ddesembolso', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Liquidación de cobranza'",'')
                      , tipo = RawSQL("select 'LC'",''))\
            .order_by('dregistro')
        
        ampl=Ampliaciones_plazo_cabecera.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False)\
            .values('cxcliente__cxcliente__ctnombre', 'notadebito__cxnotadebito', 'dregistro', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Ampliación de plazo'",'')
                      , tipo = RawSQL("select 'AP'",''))\
            .order_by('dregistro')
        
        return asgn.union(cobr,ampl)
    
    def get_context_data(self, **kwargs):
        context = super(PendientesGenerarFacturaView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class DesembolsosPendientesView(LoginRequiredMixin, generic.ListView):
    model = Desembolsos
    template_name = "contabilidad/listadesembolsospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        asgn=Desembolsos.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lcontabilizado = False, cxtipooperacion ='A')\
            .annotate(operacion = RawSQL('SELECT cxasignacion '\
                                         'FROM operaciones_asignacion asg '\
                                        'WHERE asg.id = ' + F('cxoperacion') , ''))\
            .order_by('dregistro')
        
        return asgn
    
    def get_context_data(self, **kwargs):
        context = super(DesembolsosPendientesView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

def BuscarCuentasEspeciales(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    pk = Cuentas_especiales.objects.filter(empresa = id_empresa.empresa).first()
    if pk:
        return redirect("contabilidad:asignarcuentascontables_editar", pk=pk.id)
    else:
        return redirect("contabilidad:asignarcuentascontables_nueva")

def GenerarFactura(request, pk, tipo, operacion):
    formulario={}
    cliente = {}
    base_iva=0
    base_no_iva=0
    valor_gao=0
    valor_dc=0
    valor_iva =0
    tipo_factoring = {}
    desembolso ={}
    id_cliente={}
    id_operacion={}
    porc_iva={}

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    template_name = 'contabilidad/datosgenerarfactura_form.html'
    sp = Asignacion.objects.filter(cxestado='P'
                                   , leliminado=False
                                   , empresa = id_empresa.empresa).count()
    # datos de tasa gao/dc
    gao = Tasas_factoring.objects.filter(cxtasa="GAO"
                                         , empresa = id_empresa.empresa).first()
    if not gao:
        return HttpResponse("no encontró registro de tasa de gao en tabla de tasas de factoring")

    dc = Tasas_factoring.objects.filter(cxtasa="DCAR"
                                        , empresa = id_empresa.empresa).first()
    if not dc:
        return HttpResponse("no encontró registro de tasa de descuento de catera en tabla de tasas de factoring")

    if tipo == 'LA':
        documento_origen = Operacion.objects.get(id=pk)
        valor_gao = documento_origen.ngao
        valor_dc = documento_origen.ndescuentodecartera
        tipo_factoring = documento_origen.cxtipofactoring
        valor_iva=documento_origen.niva
        desembolso=documento_origen.ddesembolso
        id_cliente=documento_origen.cxcliente
        id_operacion=documento_origen
        porc_iva=documento_origen.nporcentajeiva

    if tipo == 'AP':
        documento_origen = Ampliaciones_plazo_cabecera.objects.get(id=pk)
        valor_gao = documento_origen.ncomision
        valor_dc = documento_origen.ndescuentodecartera
        tipo_factoring = documento_origen.notadebito.cxtipofactoring
        valor_iva=documento_origen.niva
        desembolso=documento_origen.notadebito.dnotadebito
        id_cliente=documento_origen.cxcliente
        id_operacion=documento_origen
        porc_iva=documento_origen.nporcentajeiva

    if gao.lcargaiva:
        base_iva = valor_gao
    else:
        base_no_iva = valor_gao

    if dc.lcargaiva:
        base_iva += valor_dc
    else:
        base_no_iva += valor_dc

    if request.method=='GET':

        e = {
            'cxnumerofactura':'...',
            'demision': desembolso,
            'cxestado':'A',
            'niva' : valor_iva,
            'nvalor':valor_gao + valor_dc + valor_iva,
            'nbaseiva':base_iva,
            'nbasenoiva':base_no_iva,
            'nporcentajeiva':porc_iva,
            'cliente':id_cliente,
            'cxtipooperacion':tipo,
            'operacion':id_operacion,
        }

        concepto= 'COBRO DE SERVICIOS POR LA OPERACIÓN ' + operacion

        formulario = FacturaVentaForm(e, empresa = id_empresa.empresa)

        contexto={'solicitudes_pendientes':sp
                , 'form': formulario
                , 'operacion':operacion
                , 'concepto':concepto
                }    
    
        return render(request, template_name, contexto)

    if request.method == 'POST':

        with transaction.atomic():

            pe=request.POST.get("puntoemision")
            cl = request.POST.get("cliente")
            puntoemision = Puntos_emision.objects.filter(pk = pe).first()
            cliente = Datos_generales.objects.filter(pk = cl).first()

            porc_iva = request.POST.get("nporcentajeiva")
            nbaseiva=request.POST.get("nbaseiva")
            nbasenoiva=request.POST.get("nbasenoiva")
            ctconcepto = request.POST.get("concepto")
            valor = request.POST.get("nvalor")
            emision = request.POST.get("demision")
            numero_factura = request.POST.get("cxnumerofactura")
            
            factura = Factura_venta(
                cliente = cliente,
                puntoemision = puntoemision,
                cxnumerofactura = numero_factura,
                demision = emision,
                cxestado = 'A',
                cxtipodocumento = '01',
                nbasenoiva = nbasenoiva,
                nbaseiva = nbaseiva,
                niva = request.POST.get("niva"),
                nvalor = valor,
                nsaldo = valor,
                nporcentajeiva = porc_iva,
                cxtipooperacion = tipo,
                operacion = id_operacion.id,
                empresa = id_empresa.empresa,
                cxusuariocrea= request.user,
            )
            factura.save()

            # marcar como procesadas
            documento_origen.lfacturagenerada = True
            documento_origen.save()

            # grabar el detalle de la factira
            if valor_gao > 0:
                detalle_factura = Items_facturaventa(
                    factura = factura,
                    item = gao,
                    nvalor = valor_gao,
                    lcargaiva = gao.lcargaiva,
                    cxusuariocrea= request.user,
                    empresa = id_empresa.empresa,
                )
                detalle_factura.save()

            if valor_dc > 0:
                detalle_factura = Items_facturaventa(
                    factura = factura,
                    item = dc,
                    nvalor = valor_dc,
                    lcargaiva = dc.lcargaiva,
                    cxusuariocrea= request.user,
                    empresa = id_empresa.empresa,
                )
                detalle_factura.save()

            # grbar los impuestos

            if Decimal(nbaseiva) > 0:
                impuestos = Impuestos_facturaventa(
                    factura = factura,
                    cximpuesto = 'IVA',
                    cxporcentaje = porc_iva,
                    nbase = factura.nbaseiva,
                    nvalor = factura.niva,
                    cxusuariocrea= request.user,
                    empresa = id_empresa.empresa,
                    )
                impuestos.save()

            if Decimal(nbasenoiva) > 0:
                impuestos = Impuestos_facturaventa(
                    factura = factura,
                    cximpuesto = 'IVA',
                    cxporcentaje = '0',
                    nbase = factura.nbasenoiva,
                    nvalor = 0,        
                    cxusuariocrea= request.user,
                    empresa = id_empresa.empresa,
                    )
                impuestos.save()

            # actualizar contador de facturas
            pe = Puntos_emision.objects.filter(pk=puntoemision.id).first()
            pe.nultimasecuencia = pe.nultimasecuencia + 1
            pe.save()

            # grabar asiento contable
            diario = GrabarAsientoFactura(request, puntoemision,  ctconcepto
                                  , emision, valor, valor_gao, valor_dc, valor_iva
                                  , tipo_factoring, operacion, numero_factura, gao
                                  , dc, id_empresa)

            factura.cxasiento = diario
            factura.save()

        # clave de acceso
        claveacceso = time.strftime('%d%m%Y',time.strptime(factura.demision, '%Y-%m-%d')) \
            + '01' +factura.empresa.ctruccompania + '2' \
            + factura.puntoemision.cxestablecimiento \
            + factura.puntoemision.cxpuntoemision\
            + factura.cxnumerofactura.zfill(9) \
            + factura.cxnumerofactura.zfill(8) + '1'
        dv = calculate_check_digit(claveacceso)        

        claveacceso += str(dv)

        # crear el XML y bajarlo a la carpeta descargas
        documento = etree.Element('factura')
        documento.set('id','comprobante')
        documento.set('version','1.1.0')

        # generar infoTributaria
        infoTributaria = _get_tax_element(factura, claveacceso, '1')
        documento.append(infoTributaria)
        
        # generar infoFactura
        infoFactura = _get_invoice_element(factura)
        documento.append(infoFactura)
        
        #generar detalles
        detalles = _get_detail_element(factura)        
        documento.append(detalles)

        # informacion adicional
        infoAdicional = etree.Element('infoAdicional')
        campoAdicional = etree.SubElement(infoAdicional,'campoAdicional')
        campoAdicional.text=ctconcepto
        campoAdicional.set('nombre','Concepto')
        
        documento.append(infoAdicional)

        tree = etree.ElementTree(documento)

        # Set the path for the Downloads folder
        folder = os.path.join(os.path.expanduser("~"), "Downloads")

        # Set the full path for the file
        file_path = os.path.join(folder, claveacceso+".XML")

        tree.write(file_path)
        return HttpResponse(diario.id)

def ObtenerSecuenciaFactura(request,punto_emision):
    success = False
    secuencia = 0

    x = Puntos_emision.objects.filter(pk=punto_emision).first()

    if x:
        success = True
        secuencia = x.nultimasecuencia + 1

    data = {'secuencia':secuencia, 'success':success}
    return JsonResponse(data)

def GrabarAsientoFactura(request, puntoemision, ctconcepto, emision, valor
                          , valor_gao, valor_dc, valor_iva, tipo_factoring
                          , operacion, numero_factura, gao, dc, id_empresa):
    # grabar asiento de diario
    # cxc
    #   gao/dc/IVA
    # Los valores de los cargos van en las cuentas respectivas segun el tipo de factoring
    contador_diario = Contador.objects\
        .filter(cxtransaccion='AD', empresa = id_empresa.empresa).first()
    
    if contador_diario:
        x=Decimal(contador_diario.nultimonumero) + 1
        nuevo_diario = 'AD-' + str(x)
    else:
        contador_diario = Contador(cxtransaccion='AD',
                                    nultimonumero = 0,
                                    empresa = id_empresa.empresa,
                                    cxusuariocrea= request.user,
                                    )
        nuevo_diario = 'AD-1'
        
    contador_diario.nultimonumero =+ 1
    contador_diario.save()

    diario = Diario_cabecera(cxtransaccion = nuevo_diario,
                                ctconcepto = ctconcepto,
                                nvalor = valor,
                                dcontabilizado = emision,
                            empresa = id_empresa.empresa,
                            cxusuariocrea= request.user,
                                )
    diario.save()

    # grabar detalles de diario
    cuentas = Cuentas_especiales.objects.filter(empresa = id_empresa.empresa).first()

    detalle = Transaccion(diario = diario,
                            cxcuenta = cuentas.cuentaporcobrar,
                            cxtipo = 'D',
                            nvalor = valor,
                            cxreferencia = puntoemision.__str__()+'-' + numero_factura,
                        empresa = id_empresa.empresa,
                        cxusuariocrea= request.user,)
    detalle.save()

    if valor_gao:
        tasa = Cuentas_tasasfactoring.objects\
            .filter(empresa = id_empresa.empresa, leliminado = False
                    , tipofactoring = tipo_factoring, tasafactoring = gao
                    ).first()
        cta = Plan_cuentas.objects.filter(pk = tasa.cuenta.id).first()
        detalle = Transaccion(diario = diario,
                            cxcuenta = cta,
                            cxtipo = 'H',
                            nvalor = valor_gao,
                            cxreferencia = operacion,
                        empresa = id_empresa.empresa,
                        cxusuariocrea= request.user,)
    detalle.save()

    if valor_dc:
        tasa = Cuentas_tasasfactoring.objects\
            .filter(empresa = id_empresa.empresa, leliminado = False
                    , tipofactoring = tipo_factoring, tasafactoring = dc
                    ).first()
        cta = Plan_cuentas.objects.filter(pk = tasa.cuenta.id).first()
        detalle = Transaccion(diario = diario,
                            cxcuenta = cta,
                            cxtipo = 'H',
                            nvalor = valor_dc,
                            cxreferencia = operacion,
                        empresa = id_empresa.empresa,
                        cxusuariocrea= request.user,)    
                            
    detalle.save()

    if valor_iva:
        detalle = Transaccion(diario = diario,
                            cxcuenta = cuentas.cuentaivaganado,
                            cxtipo = 'H',
                            nvalor = valor_iva,
                            cxreferencia = operacion,
                        empresa = id_empresa.empresa,
                        cxusuariocrea= request.user,)

    detalle.save()

    return HttpResponse(diario)
