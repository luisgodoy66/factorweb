from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q, FilteredRelation, Max, CharField
from django.db.models.functions import Concat
from django.db.models.expressions import RawSQL , F, Value
from django.http import JsonResponse
from django.db import transaction
from django.views import generic
from django.utils.dateparse import parse_date

import json

from .models import Plan_cuentas, Cuentas_especiales, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring, Factura_venta\
    , Cuentas_diferidos, Cuentas_provisiones, Diario_cabecera, Transaccion\
    , Comprobante_egreso, Control_meses, Cuentas_cargosfactoring\
    , Cuentas_reestructuracion
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from empresa.models import Cuentas_bancarias, Tipos_factoring, Puntos_emision\
    , Contador, Tasas_factoring
from operaciones.models import Asignacion as Operacion, Movimientos_maestro\
    , Ampliaciones_plazo_cabecera, Desembolsos
from cobranzas.models import Liquidacion_cabecera, Documentos_cabecera as Cobranzas\
    , Cheques_protestados, Recuperaciones_cabecera, Factura_cuota, Pagare_cabecera
from cuentasconjuntas.models import Transferencias

from bases.views import enviarPost, SinPrivilegios

from .forms import CuentasEspecialesForm, CuentasBancosForm, FacturaVentaForm\
    , CuentasTiposFactoringForm, CuentasTasaTiposFactoringForm\
    , ComprobanteEgresoForm, CuentasDiferidoTasaTiposFactoringForm\
    , CuentasProvisionTasaTiposFactoringForm, PlanCuentasForm, DiarioCabeceraForm\
    , TransaccionForm, CuentasCargoTiposFactoringForm, CuentasReestructuracionForm

import xml.etree.cElementTree as etree
from datetime import date, timedelta, datetime

class CuentasView(SinPrivilegios, generic.ListView):
    model = Plan_cuentas
    template_name = "contabilidad/listacuentascontables.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_plan_cuentas"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Plan_cuentas.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa)\
            .order_by('cxcuenta')
        return qs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasNew(SinPrivilegios, generic.CreateView):
    model = Plan_cuentas
    template_name = "contabilidad/datoscuenta_form.html"
    context_object_name='cuentas'
    form_class = PlanCuentasForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'
    permission_required="contabilidad.add_plan_cuentas"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentasNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasEdit(SinPrivilegios, generic.UpdateView):
    model = Plan_cuentas
    template_name = "contabilidad/datoscuenta_form.html"
    context_object_name='cuentas'
    form_class = PlanCuentasForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'
    permission_required="contabilidad.change_plan_cuentas"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentasEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasEspecialesNew(SinPrivilegios, generic.CreateView):
    model = Cuentas_especiales
    template_name = "contabilidad/datoscuentasespeciales_form.html"
    context_object_name='cuentas'
    form_class = CuentasEspecialesForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'
    permission_required="contabilidad.change_cuentas_especiales"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentasEspecialesNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasEspecialesNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentasEspecialesEdit(SinPrivilegios, generic.UpdateView):
    model = Cuentas_especiales
    template_name='contabilidad/datoscuentasespeciales_form.html'
    context_object_name='cuentas'
    form_class = CuentasEspecialesForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'
    permission_required="contabilidad.change_cuentas_especiales"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(CuentasEspecialesEdit, self).get_context_data(**kwargs)
        # context["id"]=pk
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasEspecialesEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs
    
class CuentasBancosView(SinPrivilegios, generic.ListView):
    model = Cuentas_bancarias
    template_name = "contabilidad/listacuentasbancos.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_bancos"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Cuentas_bancarias.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context = super(CuentasBancosView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentaBancoNew(SinPrivilegios, generic.CreateView):
    model=Cuentas_bancos
    template_name="contabilidad/datoscuentabanco_modal.html"
    context_object_name = "consulta"
    form_class=CuentasBancosForm
    success_url=reverse_lazy("contabilidad:listacuentasbancos")
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.add_cuentas_bancos"

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

class CuentaBancoEdit(SinPrivilegios, generic.UpdateView):
    model=Cuentas_bancos
    template_name="contabilidad/datoscuentabanco_modal.html"
    context_object_name = "consulta"
    form_class=CuentasBancosForm
    success_url=reverse_lazy("contabilidad:listacuentasbancos")
    success_message="cuenta modificada satisfactoriamente"
    permission_required="contabilidad.change_cuentas_bancos"

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

class CuentasTiposFactoringView(SinPrivilegios, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_tiposfactoring"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tipos_factoring.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context = super(CuentasTiposFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentaTipoFactoringNew(SinPrivilegios, generic.CreateView):
    model=Cuentas_tiposfactoring
    template_name="contabilidad/datoscuentatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTiposFactoringForm
    success_url=reverse_lazy("contabilidad:listacuentastiposfactoring")
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.add_cuentas_tiposfactoring"

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

class CuentaTipoFactoringEdit(SinPrivilegios, generic.UpdateView):
    model=Cuentas_tiposfactoring
    template_name="contabilidad/datoscuentatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTiposFactoringForm
    success_url=reverse_lazy("contabilidad:listacuentastiposfactoring")
    success_message="cuenta modificada satisfactoriamente"
    permission_required="contabilidad.change_cuentas_tiposfactoring"

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

class CuentasTasasFactoringView(SinPrivilegios, generic.ListView):
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentastasasfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_tasasfactoring"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , litemfactura = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context = super(CuentasTasasFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasDiferidosView(SinPrivilegios, generic.ListView):
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentastasasfactoring2.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_diferidos"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , litemfactura = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context = super(CuentasDiferidosView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasProvisionesView(SinPrivilegios, generic.ListView):
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentastasasfactoring3.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_provisiones"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , litemfactura = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context = super(CuentasProvisionesView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasTasaTiposFactoringView(SinPrivilegios, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastasatiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_tiposfactoring"

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
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        id_tasa = self.kwargs.get('tasa')
        nombre_tasa = self.kwargs.get('nombre_tasa')
        context = super(CuentasTasaTiposFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp
        context["id_tasa"]=id_tasa
        context["nombre_tasa"]=nombre_tasa

        return context
    
class CuentasTasaDiferidoView(SinPrivilegios, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastasadiferido.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_diferidos"

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
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        id_tasa = self.kwargs.get('tasa')
        nombre_tasa = self.kwargs.get('nombre_tasa')
        context = super(CuentasTasaDiferidoView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp
        context["id_tasa"]=id_tasa
        context["nombre_tasa"]=nombre_tasa

        return context
    
class CuentasTasaProvisionView(SinPrivilegios, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastasaprovision.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_provisiones"

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
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        id_tasa = self.kwargs.get('tasa')
        nombre_tasa = self.kwargs.get('nombre_tasa')
        context = super(CuentasTasaProvisionView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp
        context["id_tasa"]=id_tasa
        context["nombre_tasa"]=nombre_tasa

        return context
    
class CuentaTasaTipoFactoringNew(SinPrivilegios, generic.CreateView):
    model=Cuentas_tasasfactoring
    template_name="contabilidad/datoscuentatasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTasaTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.add_cuentas_tasasfactoring"

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

class CuentaDiferidoTasaTipoFactoringNew(SinPrivilegios, generic.CreateView):
    model=Cuentas_diferidos
    template_name="contabilidad/datoscuentadiferidotasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasDiferidoTasaTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.add_cuentas_diferidos"

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
        context = super(CuentaDiferidoTasaTipoFactoringNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["tasafactoring"] = nombre_tasafactoring
        context["tasafactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaDiferidoTasaTipoFactoringNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        return reverse_lazy("contabilidad:listacuentastasadiferido"
            , kwargs={'tasa': tasafactoring_id, 'nombre_tasa':nombre_tasafactoring})

class CuentaProvisionTasaTipoFactoringNew(SinPrivilegios, generic.CreateView):
    model=Cuentas_provisiones
    template_name="contabilidad/datoscuentaprovisiontasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasProvisionTasaTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.add_cuentas_provisiones"

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
        context = super(CuentaProvisionTasaTipoFactoringNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["tasafactoring"] = nombre_tasafactoring
        context["tasafactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaProvisionTasaTipoFactoringNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        return reverse_lazy("contabilidad:listacuentastasaprovision"
            , kwargs={'tasa': tasafactoring_id, 'nombre_tasa':nombre_tasafactoring})

class CuentaTasaTipoFactoringEdit(SinPrivilegios, generic.UpdateView):
    model=Cuentas_tasasfactoring
    template_name="contabilidad/datoscuentatasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasTasaTiposFactoringForm
    success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta modificada satisfactoriamente"
    permission_required="contabilidad.change_cuentas_tasasfactoring"

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

class CuentaDiferidoTasaTipoFactoringEdit(SinPrivilegios, generic.UpdateView):
    model=Cuentas_diferidos
    template_name="contabilidad/datoscuentadiferidotasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasDiferidoTasaTiposFactoringForm
    success_message="cuenta modificada satisfactoriamente"
    permission_required="contabilidad.change_cuentas_diferidos"

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
        context = super(CuentaDiferidoTasaTipoFactoringEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["tasafactoring"] = nombre_tasafactoring
        context["tasafactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        context["pk"] = id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaDiferidoTasaTipoFactoringEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        return reverse_lazy("contabilidad:listacuentastasadiferido"
            , kwargs={'tasa': tasafactoring_id, 'nombre_tasa':nombre_tasafactoring})

class CuentaProvisionTasaTipoFactoringEdit(SinPrivilegios, generic.UpdateView):
    model=Cuentas_provisiones
    template_name="contabilidad/datoscuentaprovisiontasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasProvisionTasaTiposFactoringForm
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.change_cuentas_provisiones"

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
        context = super(CuentaProvisionTasaTipoFactoringEdit, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["tasafactoring"] = nombre_tasafactoring
        context["tasafactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaProvisionTasaTipoFactoringEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('tasafactoring_id')
        nombre_tasafactoring = self.kwargs.get('tasafactoring')
        return reverse_lazy("contabilidad:listacuentastasaprovision"
            , kwargs={'tasa': tasafactoring_id, 'nombre_tasa':nombre_tasafactoring})

class PendientesGenerarFacturaView(SinPrivilegios, generic.ListView):
    model = Plan_cuentas
    template_name = "contabilidad/listapendientesgenerarfactura.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.add_factura_venta"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        asgn=Operacion.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False
                    , cxtipofactoring__lgenerafacturaenaceptacion = True)\
            .values('cxcliente__cxcliente__ctnombre', 'cxasignacion'
                    , 'ddesembolso', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Asignación'",'')
                      , tipo = RawSQL("select 'LA'",'')
                      , facturar = F('ngao')+ F('ndescuentodecartera')+F('notroscargos'))\
            .order_by('dregistro')
        
        cobr=Liquidacion_cabecera.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False)\
            .values('cxcliente__cxcliente__ctnombre', 'cxliquidacion'
                    , 'ddesembolso', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Liquidación de cobranza'",'')
                      , tipo = RawSQL("select 'LC'",'')
                      , facturar = F('ngaoa')
                        + F('ngao')
                        + F('ndescuentodecartera') 
                        + F('ndescuentodecarteravencido')
                        + F('notroscargos'))\
            .filter(facturar__gt=0)\
            .order_by('dregistro')
        
        ampl=Ampliaciones_plazo_cabecera.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False)\
            .values('cxcliente__cxcliente__ctnombre', 'notadebito__cxnotadebito'
                    , 'dregistro', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Ampliación de plazo'",'')
                      , tipo = RawSQL("select 'AP'",'')
                      , facturar = F('nvalor'))\
            .order_by('dregistro')
        
        paga=Factura_cuota.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False)\
            .values('cuota__pagare__cxcliente__cxcliente__ctnombre', 'cobranzacuota__cobranza__cxcobranza'
                    , 'dregistro', 'id')\
            .annotate(tipo_operacion = RawSQL("select 'Cobro de pagaré'",'')
                      , tipo = RawSQL("select 'CP'",'')
                      , facturar = F('nbaseiva') + F('nbasenoiva'))\
            .order_by('dregistro')

        return asgn.union(cobr,ampl, paga)
    
    def get_context_data(self, **kwargs):
        context = super(PendientesGenerarFacturaView, self).get_context_data(**kwargs)
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class DesembolsosPendientesView(SinPrivilegios, generic.ListView):
    model = Desembolsos
    template_name = "contabilidad/listadesembolsospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.add_comprobante_egreso"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        asgn=Desembolsos.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lcontabilizado = False, cxtipooperacion ='A')\
            .values('id','cxcliente__cxcliente__ctnombre'
                    , 'nvalor', 'cxformapago', 'cxcuentapago__cxbanco__ctbanco')\
            .annotate(operacion = RawSQL('SELECT cxasignacion '\
                                        'FROM operaciones_asignacion asgn '\
                                        'WHERE asgn.id = cxoperacion',''))\
            .order_by('dregistro')
        
        cobr=Desembolsos.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lcontabilizado = False, cxtipooperacion ='C')\
            .values('id','cxcliente__cxcliente__ctnombre'
                    , 'nvalor', 'cxformapago', 'cxcuentapago__cxbanco__ctbanco')\
            .annotate(operacion = RawSQL('SELECT cxliquidacion '\
                                        'FROM cobranzas_liquidacion_cabecera liq '\
                                        'WHERE liq.id = cxoperacion',''))\
            .order_by('dregistro')
        
        return asgn.union(cobr)
    
    def get_context_data(self, **kwargs):
        context = super(DesembolsosPendientesView, self).get_context_data(**kwargs)
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class AsientosView(SinPrivilegios, generic.ListView):
    model = Diario_cabecera
    template_name = "contabilidad/listaasientoscontables.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_diario_cabecera"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        desde = date.today() + timedelta(-1)
        hasta = date.today() + timedelta(1)
        qs=Diario_cabecera.objects\
            .filter( dregistro__gte = desde, dregistro__lte = hasta
                    , empresa = id_empresa.empresa)\
            .order_by('dcontabilizado')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(AsientosView, self).get_context_data(**kwargs)
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class DiariosConsulta(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/consultageneralasientos.html"
    login_url = 'bases:login'
    permission_required="contabilidad.view_diario_cabecera"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(DiariosConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context
 
class LibroMayorConsulta(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/consultalibromayor.html"
    permission_required="contabilidad.view_transaccion"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(LibroMayorConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] =hasta
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        context['cuentas'] = Plan_cuentas.objects\
            .filter(empresa= id_empresa.empresa, nnivel__gte= 4, leliminado= False)\
            .order_by('cxcuenta')
        return context

class ListaCobranzasAGenerar(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/listacobranzaspendientescontabilizar.html"
    login_url = 'bases:login'
    permission_required="contabilidad.add_diario_cabecera"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        context = super(ListaCobranzasAGenerar, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        context['solicitudes_pendientes'] = sp
        return context
 
class BalanceGeneralConsulta(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/consultabalancegeneral.html"
    permission_required="contabilidad.view_saldos"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        mescerrado = Control_meses.objects\
            .filter(lbloqueado = True, empresa = id_empresa.empresa)\
            .values('empresa')\
            .annotate(ultimomes = Max(Concat('año','mes')))

        if mescerrado:
            añomes = mescerrado[0]['ultimomes']
            año = int(añomes[0:4])
            mes = int(añomes[4:6])
            if mes < 12:
                mes +=1
            else:
                mes = 1
                año += 1
        else:
            año = datetime.now().year
            mes = datetime.now().month

        context = super(BalanceGeneralConsulta, self).get_context_data(**kwargs)
        context['solicitudes_pendientes'] = sp
        context['año'] = año
        context['mes'] = mes

        return context

class PerdiasyGananciasConsulta(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/consultaperdidasyganancias.html"
    permission_required="contabilidad.view_saldos_gyp"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        mescerrado = Control_meses.objects.filter(lbloqueado = True, empresa = id_empresa.empresa)\
            .values('empresa')\
            .annotate(ultimomes = Max(Concat('año','mes')))

        if mescerrado:
            añomes = mescerrado[0]['ultimomes']
            año = int(añomes[0:4])
            mes = int(añomes[4:6])
            if mes < 12:
                mes +=1
            else:
                mes = 1
                año += 1
        else:
            año = datetime.now().year
            mes = datetime.now().month

        context = super(PerdiasyGananciasConsulta, self).get_context_data(**kwargs)
        context['solicitudes_pendientes'] = sp
        context['año'] = año
        context['mes'] = mes

        return context

class FacturasConsulta(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/consultageneralfacturas.html"
    permission_required="contabilidad.view_factura_venta"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        context = super(FacturasConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] =hasta
        context['solicitudes_pendientes'] = sp
        context['ambiente']= id_empresa.empresa.ambientesri

        return context

class ListaProtestosAGenerar(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/listaprotestospendientescontabilizar.html"
    login_url = 'bases:login'
    permission_required="contabilidad.add_diario_cabecera"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        context = super(ListaProtestosAGenerar, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        context['solicitudes_pendientes'] = sp
        return context
 
class CuentasCargosFactoringView(SinPrivilegios, generic.ListView):
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentascargosfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_cargosfactoring"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , lcargo = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context = super(CuentasCargosFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasCargoTiposFactoringView(SinPrivilegios, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentascargotiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="contabilidad.view_cuentas_cargosfactoring"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        id_cargo = self.kwargs.get('cargo')
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
                    , cuenta_cargotipofactoring__cargo = id_cargo)\
            .values('id', 'cttipofactoring'
                    ,'cuenta_cargotipofactoring__cuenta__ctcuenta'
                    ,'cuenta_cargotipofactoring'
                    ,'cuenta_cargotipofactoring__cargo')
        
        qs2=Tipos_factoring.objects\
            .annotate(registros=FilteredRelation('cuenta_cargotipofactoring'
                                                 , condition = Q(cuenta_cargotipofactoring__cargo=id_cargo)))\
            .values('id','cttipofactoring'
                    , 'registros__cuenta__ctcuenta'
                    ,'cuenta_cargotipofactoring'
                    ,'cuenta_cargotipofactoring__cargo')\
            .filter(empresa = id_empresa.empresa, registros__cuenta__ctcuenta__isnull=True)
        return qs.union(qs2)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        id_tasa = self.kwargs.get('cargo')
        nombre_tasa = self.kwargs.get('nombre_cargo')
        context = super(CuentasCargoTiposFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp
        context["id_cargo"]=id_tasa
        context["nombre_cargo"]=nombre_tasa

        return context
    
class CuentaCargoTipoFactoringNew(SinPrivilegios, generic.CreateView):
    model=Cuentas_tasasfactoring
    template_name="contabilidad/datoscuentacargotipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasCargoTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta creada satisfactoriamente"
    permission_required="contabilidad.add_cuentas_cargosfactoring"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        tasafactoring_id = self.kwargs.get('cargofactoring_id')
        nombre_tasafactoring = self.kwargs.get('cargofactoring')
        tipofactoring_id = self.kwargs.get('tipofactoring_id')
        nombre_tipofactoring = self.kwargs.get('tipofactoring')
        context = super(CuentaCargoTipoFactoringNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["cargofactoring"] = nombre_tasafactoring
        context["cargofactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaCargoTipoFactoringNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('cargofactoring_id')
        nombre_tasafactoring = self.kwargs.get('cargofactoring')
        return reverse_lazy("contabilidad:listacuentascargotiposfactoring"
            , kwargs={'cargo': tasafactoring_id, 'nombre_cargo':nombre_tasafactoring})

class CuentaCargoTipoFactoringEdit(SinPrivilegios, generic.UpdateView):
    model=Cuentas_cargosfactoring
    template_name="contabilidad/datoscuentacargotipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasCargoTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
    success_message="cuenta modificada satisfactoriamente"
    permission_required="contabilidad.change_cuentas_cargosfactoring"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        tasafactoring_id = self.kwargs.get('cargofactoring_id')
        nombre_tasafactoring = self.kwargs.get('cargofactoring')
        tipofactoring_id = self.kwargs.get('tipofactoring_id')
        nombre_tipofactoring = self.kwargs.get('tipofactoring')
        context = super(CuentaCargoTipoFactoringEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["cargofactoring"] = nombre_tasafactoring
        context["cargofactoring_id"] = tasafactoring_id
        context["tipofactoring"] = nombre_tipofactoring
        context["tipofactoring_id"] = tipofactoring_id
        context["pk"] = id
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentaCargoTipoFactoringEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_success_url(self):
        tasafactoring_id = self.kwargs.get('cargofactoring_id')
        nombre_tasafactoring = self.kwargs.get('cargofactoring')
        return reverse_lazy("contabilidad:listacuentascargotiposfactoring"
            , kwargs={'cargo': tasafactoring_id, 'nombre_cargo':nombre_tasafactoring})

class ListaTransferenciasAGenerar(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/listatransferenciaspendientescontabilizar.html"
    login_url = 'bases:login'
    permission_required="contabilidad.add_diario_cabecera"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        context = super(ListaTransferenciasAGenerar, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        context['solicitudes_pendientes'] = sp
        return context

class ListaRecuperacionesAGenerar(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/listarecuperacionespendientescontabilizar.html"
    login_url = 'bases:login'
    permission_required="contabilidad.add_diario_cabecera"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        context = super(ListaRecuperacionesAGenerar, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        context['solicitudes_pendientes'] = sp
        return context
 
class DesbloquearMes(SinPrivilegios, generic.TemplateView):
    template_name = "contabilidad/datosdesbloquearmes.html"
    permission_required="contabilidad.view_saldos"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

        mescerrado = Control_meses.objects\
            .filter(lbloqueado = True, empresa = id_empresa.empresa)\
            .values('empresa')\
            .annotate(ultimomes = Max(Concat('año','mes')))
        print(mescerrado)
        if mescerrado:
            añomes = mescerrado[0]['ultimomes']
            año = añomes[0:4]
            mes = int(añomes[4:6])
        else:
            return HttpResponse("Ningún mes encontrado como cerrado.")

        context = super(DesbloquearMes, self).get_context_data(**kwargs)
        context['solicitudes_pendientes'] = sp
        context['año'] = año
        context['mes'] = mes

        return context

class CuentasReestructuracionNew(SinPrivilegios, generic.CreateView):
    model = Cuentas_reestructuracion
    template_name = "contabilidad/datoscuentasreestructuracion_form.html"
    context_object_name='cuentas'
    form_class = CuentasReestructuracionForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'
    permission_required="contabilidad.change_cuentas_reestructuracion"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentasReestructuracionNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasReestructuracionNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentasReestructuracionEdit(SinPrivilegios, generic.UpdateView):
    model = Cuentas_reestructuracion
    template_name='contabilidad/datoscuentasreestructuracion_form.html'
    context_object_name='cuentas'
    form_class = CuentasReestructuracionForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'
    permission_required="contabilidad.change_cuentas_reestructuracion"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(CuentasReestructuracionEdit, self).get_context_data(**kwargs)
        # context["id"]=pk
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasReestructuracionEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs
    
@login_required(login_url='/login/')
@permission_required('contabilidad.view_cuentas_especiales', login_url='bases:sin_permisos')
def BuscarCuentasEspeciales(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    pk = Cuentas_especiales.objects.filter(empresa = id_empresa.empresa).first()
    if pk:
        return redirect("contabilidad:asignarcuentascontables_editar", pk=pk.id)
    else:
        return redirect("contabilidad:asignarcuentascontables_nueva")

@login_required(login_url='/login/')
@permission_required('contabilidad.add_factura_venta', login_url='bases:sin_permisos')
def GenerarFactura(request, pk, tipo, operacion):
    template_name = 'contabilidad/datosgenerarfactura_form.html'
    formulario={}
    base_iva=0
    base_no_iva=0
    valor_gao=0
    valor_dc=0
    valor_dcv=0
    valor_gaoa=0
    valor_iva =0
    desembolso ={}
    id_cliente={}
    id_operacion={}
    porc_iva={}

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

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

    gaoa = Tasas_factoring.objects.filter(cxtasa="GAOA"
                                         , empresa = id_empresa.empresa).first()
    if not gaoa:
        return HttpResponse("no encontró registro de tasa de gao adicional en tabla de tasas de factoring")

    if tipo == 'LA':
        documento_origen = Operacion.objects.get(id=pk)
        valor_gao = documento_origen.ngao
        valor_dc = documento_origen.ndescuentodecartera
        # valor_iva=documento_origen.niva
        desembolso=documento_origen.ddesembolso

    if tipo == 'LC':
        documento_origen = Liquidacion_cabecera.objects.get(id=pk)
        valor_gao = documento_origen.ngao
        valor_dc = documento_origen.ndescuentodecartera
        valor_dcv = documento_origen.ndescuentodecarteravencido
        valor_gaoa = documento_origen.ngaoa
        # valor_iva=documento_origen.niva
        desembolso=documento_origen.ddesembolso

    if tipo == 'AP':
        documento_origen = Ampliaciones_plazo_cabecera.objects.get(id=pk)
        valor_gaoa = documento_origen.ncomision
        valor_dcv = documento_origen.ndescuentodecartera
        # valor_iva=documento_origen.niva
        desembolso=documento_origen.notadebito.dnotadebito

    if tipo == 'CP':
        documento_origen = Factura_cuota.objects.get(id=pk)
        desembolso=documento_origen.cobranzacuota.cobranza.dcobranza

    if tipo == 'AP':
        if gao.lcargaiva:
            base_iva = valor_gao
        else:
            base_no_iva = valor_gao

        if dc.lcargaiva:
            base_iva += valor_dc + valor_dcv
        else:
            base_no_iva += valor_dc + valor_dcv

        if gaoa.lcargaiva:
            base_iva += valor_gaoa
        else:
            base_no_iva += valor_gaoa
    else:
        base_iva = documento_origen.nbaseiva
        base_no_iva = documento_origen.nbasenoiva

    if tipo == 'CP':
        id_operacion = documento_origen.id
        id_cliente = documento_origen.cuota.pagare.cxcliente
        porc_iva = 15
        cliente = documento_origen.cuota.pagare.cxcliente.cxcliente.ctnombre
    else:
        id_operacion = documento_origen.id  
        id_cliente = documento_origen.cxcliente
        porc_iva = documento_origen.nporcentajeiva
        cliente = documento_origen.cxcliente.cxcliente.ctnombre

    valor_iva = round(base_iva  * porc_iva / 100, 2)

    if request.method=='GET':

        e = {
            'cxnumerofactura':'...',
            'demision': desembolso,
            'cxestado':'A',
            'niva' : valor_iva,
            'nvalor':base_iva + base_no_iva + valor_iva,
            'nbaseiva':base_iva,
            'nbasenoiva':base_no_iva,
            'nporcentajeiva':porc_iva,
            'cliente':id_cliente,
        }

        concepto= 'SERVICIOS ENTREGADOS A ' + cliente + ' POR LA OPERACIÓN ' + operacion

        formulario = FacturaVentaForm(e, empresa = id_empresa.empresa)

        contexto={'solicitudes_pendientes':sp
                , 'form': formulario
                , 'operacion':operacion
                , 'concepto':concepto
                , 'cxtipooperacion':tipo
                , 'id_operacion':id_operacion
                , 'valor_gao':valor_gao 
                , 'valor_dc': valor_dc 
                , 'valor_dcv': valor_dcv
                , 'valor_gaoa': valor_gaoa
                , 'ambiente': id_empresa.empresa.ambientesri
                }    
    
    return render(request, template_name, contexto)

def ObtenerSecuenciaFactura(request,punto_emision):
    success = False
    secuencia = 0

    x = Puntos_emision.objects.filter(pk=punto_emision).first()

    if x:
        success = True
        secuencia = x.nultimasecuencia + 1

    data = {'secuencia':secuencia, 'success':success}
    return JsonResponse(data)

@login_required(login_url='/login/')
@permission_required('contabilidad.add_comprobante_egreso', login_url='bases:sin_permisos')
def GenerarComprobanteEgreso(request, pk, forma_pago, operacion):
    formulario={}
    desembolso ={}
    id_factura = None

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    template_name = 'contabilidad/datosgeneraegreso_form.html'
    
    sp = Asignacion.objects.filter(cxestado='P'
                                   , leliminado=False
                                   , empresa = id_empresa.empresa).count()

    desembolso = Desembolsos.objects.get(id=pk)

    if desembolso.cxtipooperacion =='A':
        documento_origen = Operacion.objects.filter(pk = desembolso.cxoperacion).first()        
    else:
        documento_origen = Liquidacion_cabecera.objects.filter(pk = desembolso.cxoperacion).first()

    cliente = documento_origen.cxcliente.cxcliente.ctnombre

    if not documento_origen:
        return HttpResponse("Documento " + str(desembolso.cxoperacion) + " no encontrado.")

    # determinar si tipo de factoring de la operacion requiere que se emita la factura en la negociacion
    if desembolso.cxtipooperacion=='A':
        if documento_origen.cxtipofactoring.lgenerafacturaenaceptacion:            
            factura = Factura_venta.objects\
                .filter(cxtipooperacion = 'LA'
                        , operacion = desembolso.cxoperacion).first()
            if not factura:
                return HttpResponse("Factura no encontrada o generada para esta asignación. Genere primero la factura.")

            id_factura = factura.id

    else:
        # si es liquidación de cobranza, podría no haber factura si los cargos se cobran en la negociación
        if documento_origen.facturar() > 0:
            factura = Factura_venta.objects\
                .filter(cxtipooperacion = 'LC'
                        , operacion = desembolso.cxoperacion).first()

            if not factura:
                return HttpResponse("Factura no encontrada o generada para esta liquidación. Genere primero la factura.")

            id_factura = factura.id

    if request.method=='GET':

        e = {
            'demision': documento_origen.ddesembolso,
            'cxbeneficiario':desembolso.cxbeneficiario,
            'ctrecibidopor':desembolso.ctbeneficiario,
            'cxcuentapago':desembolso.cxcuentapago,
            'cxcuentadestino': desembolso.cxcuentadestino,
            'cxformapago':desembolso.cxformapago,
            'nvalor': desembolso.nvalor,
        }

        concepto= 'PAGO DE LIQUIDACIÓN A ' + cliente +' POR LA OPERACIÓN ' + operacion

        formulario = ComprobanteEgresoForm(e
                                           , empresa = id_empresa.empresa
                                           , id_cliente=documento_origen.cxcliente.id)

        contexto={'solicitudes_pendientes':sp
                , 'form': formulario
                , 'operacion':operacion
                , 'concepto':concepto
                , 'forma_pago':forma_pago
                , 'id_desembolso':pk
                , 'id_factura': id_factura
                }    
    
        return render(request, template_name, contexto)

def GenerarFacturaDiario(request):
    # ejecuta un store procedure 
    pslocalidad = ''

    objeto=json.loads(request.body.decode("utf-8"))

    pstipo_operacion =objeto["tipo_operacion"]
    pid_operacion =objeto["id_operacion"]
    pid_puntoemision =objeto["id_puntoemision"]
    pid_cliente = objeto["id_cliente"]
    pnbase_iva = objeto["base_iva"]
    pnbase_noiva = objeto["base_noiva"]
    psconcepto = objeto["concepto"]
    pdemision  = objeto["emision"]
    pngao=objeto["ngao"]
    pndescuentocartera=objeto["ndescuentocartera"]
    pndescuentocarteravencido=objeto["ndescuentocarteravencido"]
    pngaoa=objeto["ngaoa"]
    pniva=objeto["niva"]
    nusuario = request.user.id
    porcentaje_iva = objeto["porcentaje_iva"]
    secuencia = objeto["secuencia"]

    if pstipo_operacion != 'CP':
        resultado=enviarPost("CALL uspGenerarFacturaContabilidad( '{0}',{1},{2},{3}\
                            ,{4},{5},{6},'{7}',{8}\
                            ,{9},{10},{11},'{12}'\
                            ,{13},{14}, {15},'',0)"
            .format(pstipo_operacion,pid_operacion,pid_puntoemision,pid_cliente\
                    , pnbase_iva, pnbase_noiva, pniva, psconcepto, pngao\
                ,pndescuentocartera, pngaoa, pndescuentocarteravencido, pdemision
                , porcentaje_iva, nusuario, secuencia))
    else:
        resultado=enviarPost("CALL uspGenerarFacturaContabilidadCobroCuota( '{0}'\
                             ,{1},{2},{3}\
                            ,{4},{5},{6},'{7}','{8}'\
                            ,{9},{10}, {11},'',0)"
            .format(pstipo_operacion
                    , pid_operacion,pid_puntoemision,pid_cliente
                    , pnbase_iva, pnbase_noiva, pniva, psconcepto, pdemision
                , porcentaje_iva, nusuario, secuencia))

    return HttpResponse(resultado)

def GenerarEgresoDiario(request):
    # ejecuta un store procedure 
    pslocalidad = ''

    objeto=json.loads(request.body.decode("utf-8"))

    psforma_pago = objeto["psforma_pago"]
    pid_desembolso = objeto["pid_desembolso"]
    pscxbeneficiario = objeto["pscxbeneficiario"]
    psrecibidopor = objeto["psrecibidopor"] 
    pid_cuentapago = objeto["pid_cuentapago"] 
    pscheque = objeto["pscheque"] 
    pid_cuentadestino = objeto["pid_cuentadestino"]
    psconcepto = objeto["concepto"]
    pdemision = objeto["pdemision"]
    pnvalor = objeto["pnvalor"]
    pid_factura = objeto["pid_factura"]
    nusuario = request.user.id

    # para los casos donde no se emite factura en la negociación, esta tendrá 
    # valor null
    if pid_factura =='None':
        pid_factura= 'NULL'
    # LA CUENTA de pago es null cuando es movimiento contable
    if not pid_cuentapago:
        pid_cuentapago='NULL'

    resultado=enviarPost("CALL uspGenerarEgresoContabilidad( '{0}',{1},'{2}','{3}'\
                         ,{4},'{5}',{6},'{7}','{8}'\
                         ,{9},{10},{11},'',0)"
        .format(psforma_pago, pid_desembolso, pscxbeneficiario, psrecibidopor\
                , pid_cuentapago, pscheque, pid_cuentadestino, psconcepto, pdemision\
            ,pnvalor, pid_factura, nusuario))
    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('contabilidad.add_diario_cabecera', login_url='bases:sin_permisos')
def AsientoDiario(request, diario_id = None):

    template_name="contabilidad/datosasiento_form.html"
    diario_form = DiarioCabeceraForm()

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                    empresa = id_empresa.empresa).count()

    if request.method =='GET':
        d = Diario_cabecera.objects.filter(pk = diario_id).first()
        if d:
            diario_form = DiarioCabeceraForm(instance=d, )  

        contexto={'form_diario': diario_form,
                'diario':diario_id,
                'solicitudes_pendientes':sp
        }
    
        return render(request, template_name, contexto)

    if request.method=='POST':

        fecha = request.POST.get("dcontabilizado")
        concepto = request.POST.get("ctconcepto")
        valor =  request.POST.get("total_debe")

        # inicio de transaccion
        with transaction.atomic():

            if not diario_id:
                # buscar el secuancial que toca
                sec = Contador.objects.filter(cxtransaccion = 'AD'
                                              , empresa = id_empresa.empresa)\
                                              .first()
                if sec:
                    contador = sec.nultimonumero + 1
                else:
                    contador = 1
                    # crear el contador si no existe
                    sec = Contador(
                        cxtransaccion = 'AD',
                        nultimonumero = 0,
                        empresa = id_empresa.empresa,
                        cxusuariocrea = request.user,
                    )
                # agregar ceros a la izquierda de variable numerica en python?

                transaccion = 'AD-' + str(contador).zfill(7)

                diario = Diario_cabecera(
                    cxtransaccion = transaccion,
                    dcontabilizado = fecha,
                    ctconcepto = concepto,
                    nvalor = valor,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if diario:
                    diario.save()
                    diario_id = diario.id

                # actualizar la secuencia de diarios
                sec.nultimonumero = contador
                sec.save()

                # nueva = True
            else:
                diario = Diario_cabecera.objects.filter(pk= diario_id).first()
                if diario:

                    diario.dcontabilizado = fecha
                    diario.ctconcepto = concepto
                    diario.nvalor = valor
                    diario.cxusuariomodifica = request.user.id
                    diario.save()

                # nueva = False

            if not diario_id:
                return redirect("contabilidad:listaasientoscontables")

            # grabar detalle 

            # recuperar el string de lista  pasado en la data y
            # convertir a lista
            lista = request.POST.get("Diario")
            output = eval(lista)

            for elem in output:      
                #accedemos a cada elemento de la lista (en este caso cada elemento es un dictionario)
                id_linea =  elem.get("id_linea")

                cuenta = Plan_cuentas.objects\
                    .filter(id = elem.get("cuenta")).first()

                if elem.get("tipo") =='D':
                    nvalor = float(elem.get("debe"))
                else:
                    nvalor = float(elem.get("haber"))

                if id_linea == '0':
                    detalle = Transaccion(
                        diario = diario,
                        cxcuenta=cuenta,
                        cxtipo = elem.get("tipo"),
                        nvalor = nvalor,
                        ctreferencia = elem.get("referencia"),
                        cxusuariocrea = request.user,
                        empresa = id_empresa.empresa,
                    )
                else:
                    detalle = Transaccion.objects\
                        .filter(id = id_linea).first()
                    
                    if detalle:
                        print("valor", nvalor, nvalor != 0.00)
                        if nvalor != 0.00:
                            detalle.cxcuenta=cuenta
                            detalle.cxtipo = elem.get("tipo")
                            detalle.nvalor = nvalor
                            detalle.ctreferencia = elem.get("referencia")
                            detalle.cxusuariomodifica = request.user.id
                        else:
                            detalle.leliminado = True
                            detalle.cxusuarioelimina = request.user.id
                
                if detalle:
                    detalle.save()
            
        # la ejecucion de esta vista POST se hace por jquery.ajax 
        # y ese proceso imprime el asiento y devuelve a la lista de asientos
        return HttpResponse( diario_id)
    
@login_required(login_url='/login/')
@permission_required('contabilidad.view_plan_cuentas', login_url='bases:sin_permisos')
def DatosLineaDiarioEditar(request, detalle_id = None):

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    template_name = "contabilidad/datoslineaasiento_modal.html"

    form_linea = TransaccionForm(empresa=id_empresa.empresa)
    
    if request.method=='GET':
        if detalle_id:
            detalle = Transaccion.objects.get(id=detalle_id)
            e = {'cxcuenta':detalle.cxcuenta
                , 'cxtipo':detalle.cxtipo
                , 'ctreferencia':detalle.ctreferencia
                , 'nvalor':detalle.nvalor}
            
            form_linea = TransaccionForm(e, empresa=id_empresa.empresa)

    contexto={'form_linea': form_linea,
              'detalle_id': detalle_id,
              'valor': 0,
    }

    return render(request, template_name, contexto)

def GeneraListaDiariosJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        diario = Diario_cabecera.objects\
            .filter(empresa = id_empresa.empresa).order_by('dcontabilizado')
    else:
        diario = Diario_cabecera.objects\
            .filter(dcontabilizado__gte = desde, dcontabilizado__lte = hasta
                    , empresa = id_empresa.empresa)\
            .order_by('dcontabilizado')
        
    tempBlogs = []
    for i in range(len(diario)):
        tempBlogs.append(GeneraListaDiariosJSONSalida(diario[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": diario.count(),
        "totalNotFiltered": diario.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaDiariosJSONSalida(diario):
    output = {}

    output["id"] = diario.id
    output["Diario"] = diario.cxtransaccion
    output["Fecha"] = diario.dcontabilizado.strftime("%Y-%m-%d")
    output["Concepto"] = diario.ctconcepto
    output["Valor"] = diario.nvalor

    factura = Factura_venta.objects.filter(asiento = diario.id).first()
    if factura:
        output["Factura"] = factura.__str__()
        output["RecibidoPor"] = None
        output["Tipo"] = 'D'
    else:
        output["Factura"] = None

        ce = Comprobante_egreso.objects.filter(asiento = diario.id).first()
        if ce : 
            output["RecibidoPor"] =  ce.ctrecibidopor
            output["Tipo"] = 'E'
        else:
            output["RecibidoPor"] = None
            output["Tipo"] = 'D'

    output["Estado"] = diario.cxestado
    output["Registro"] = diario.dregistro

    return output

def GeneraLibroMayorJSON(request, desde = None, hasta= None, cuentas = None):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    arr_cuentas = []
    id_cuenta=""

    ids = cuentas.split(',')
    for id in ids:
        arr_cuentas.append(id)

    if desde == 'None':
        detalle_asiento = Transaccion.objects\
            .filter(cxcuenta__id__in =cuentas, leliminado = False
                    ,empresa = id_empresa.empresa)\
            .order_by('cxcuenta','diario__dcontabilizado')
    else:
        detalle_asiento = Transaccion.objects\
            .filter(diario__dcontabilizado__gte = desde
                    , diario__dcontabilizado__lte = hasta
                    , leliminado = False
                    , cxcuenta__id__in = arr_cuentas
                    , empresa = id_empresa.empresa)\
            .order_by('cxcuenta','diario__dcontabilizado')
            
    tempBlogs = []
    nsaldo={}

    for i in range(len(detalle_asiento)):
        # por cada cuenta mostrar saldo aterior
        if detalle_asiento[i].cxcuenta!=id_cuenta:
            if id_cuenta!="":
                tempBlogs.append({}) 
            id_cuenta = detalle_asiento[i].cxcuenta
            # convertir string en tipo fecha?
            fecha_desde = datetime.strptime(desde,"%Y-%m-%d")
            result = enviarPost("CALL uspSaldoCuenta({0},'{1}','',0)".format(detalle_asiento[i].cxcuenta.id
                                                                        ,fecha_desde - timedelta(days=1)))
            if result[0] !='':
                return result[0]
            
            output = {}
            nsaldo["valor"] = result[1]
            output["Concepto"] = '*** '+detalle_asiento[i].cxcuenta.__str__()+' ***'
            output["Referencia"] = "SALDO ANTERIOR"
            output["Saldo"] = nsaldo["valor"]
            tempBlogs.append(output) 

        tempBlogs.append(GeneraLibroMayorJSONSalida(detalle_asiento[i], nsaldo)) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": detalle_asiento.count(),
        "totalNotFiltered": detalle_asiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraLibroMayorJSONSalida(detalle, saldo):
    output = {}
    nsaldo = saldo["valor"]

    output["id"] = detalle.id
    output["Cuenta"] =  detalle.cxcuenta.__str__()
    output["Fecha"] = detalle.diario.dcontabilizado
    output["Asiento"] = detalle.diario.cxtransaccion
    output["Concepto"] = detalle.diario.ctconcepto
    output["Referencia"] = detalle.ctreferencia
    if detalle.cxtipo=='D':
        output["Debe"] = detalle.nvalor
    else:
        output["Haber"] = detalle.nvalor

    factura = Factura_venta.objects.filter(asiento = detalle.diario.id).first()
    if factura:
        output["Tipo"] = 'D'
    else:
        ce = Comprobante_egreso.objects.filter(asiento = detalle.diario.id).first()
        if ce : 
            output["Tipo"] = 'E'
        else:
            output["Tipo"] = 'D'
    output["Diario"] = detalle.diario.id
    
    # sumar o restar dependiendo del tipo de cuenta
    if detalle.cxcuenta.activo_egreso():
        if detalle.cxtipo=='D':
            nsaldo += detalle.nvalor
        else:
            nsaldo -= detalle.nvalor
    else:
        if detalle.cxtipo=='H':
            nsaldo += detalle.nvalor
        else:
            nsaldo -= detalle.nvalor

    output["Saldo"] = nsaldo
    saldo["valor"] = nsaldo

    return output

@login_required(login_url='/login/')
@permission_required('contabilidad.change_diario_cabecera', login_url='bases:sin_permisos')
def ReversarAsiento(request, pk):
    # marcar el detalle de transaccion como la cabecera de aasiento
    asiento = Diario_cabecera.objects.filter(pk = pk).first()

    asiento.leliminado = True
    asiento.cxusuarioelimina = request.user.id
    asiento.cxestado="E"
    asiento.save()

    for d in Transaccion.objects.filter(diario = pk):
        d.leliminado= True
        d.cxusuarioelimina = request.user.id
        d.save()
    
    return HttpResponse("OK")

def GeneraListaCobranzasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        cartera = Cobranzas.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , empresa = id_empresa.empresa)\
            .values('dcobranza', 'id', 'cxcobranza', 'nsobrepago'
                    ,'cxcliente__cxcliente__ctnombre'
                    ,'nvalor'
                    , 'cxcuentadeposito__cxbanco__ctbanco'
                    , 'cxcuentadeposito__cxcuenta'
                    , 'ldepositoencuentaconjunta'
                    ,'cxtipofactoring__ctabreviacion'
                    )
        
        cobrocuotas = Pagare_cabecera.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , empresa = id_empresa.empresa)\
            .values('dcobranza', 'id', 'cxcobranza', 'nsobrepago'
                    ,'cxcliente__cxcliente__ctnombre'
                    ,'nvalor'
                    , 'cxcuentadeposito__cxbanco__ctbanco'
                    , 'cxcuentadeposito__cxcuenta'
                    )\
            .annotate(depositoencuentaconjunta = RawSQL("select False",'')
                        ,tipo=RawSQL("select 'PAGARE'",'')
                        )
                    
    else:
        cartera = Cobranzas.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , dcobranza__gte = desde, dcobranza__lte = hasta
                    , empresa = id_empresa.empresa)\
            .values('dcobranza', 'id', 'cxcobranza', 'nsobrepago'
                    ,'cxcliente__cxcliente__ctnombre'
                    ,'nvalor'
                    , 'cxcuentadeposito__cxbanco__ctbanco'
                    , 'cxcuentadeposito__cxcuenta'
                    , 'ldepositoencuentaconjunta'
                    ,'cxtipofactoring__ctabreviacion'
                    )

        cobrocuotas = Pagare_cabecera.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , empresa = id_empresa.empresa)\
            .values('dcobranza', 'id', 'cxcobranza', 'nsobrepago'
                    ,'cxcliente__cxcliente__ctnombre'
                    ,'nvalor'
                    , 'cxcuentadeposito__cxbanco__ctbanco'
                    , 'cxcuentadeposito__cxcuenta'
                    )\
            .annotate(depositoencuentaconjunta = RawSQL("select False",'')
                        ,tipo=RawSQL("select 'PAGARE'",'')
                        )
    cobranzas = cartera.union(cobrocuotas).order_by('dcobranza')    

    tempBlogs = []
    for i in range(len(cobranzas)):
        tempBlogs.append(GeneraListaCobranzasJSONSalida(cobranzas[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": cobranzas.count(),
        "totalNotFiltered": cobranzas.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaCobranzasJSONSalida(cobranza):
    output = {}

    output["id"] = cobranza['id']
    output["Fecha"] = cobranza['dcobranza'].strftime("%Y-%m-%d")
    output["Cliente"] = cobranza['cxcliente__cxcliente__ctnombre']
    output["Valor"] = cobranza['nvalor']
    output["TipoFactoring"] = cobranza['cxtipofactoring__ctabreviacion']
    if cobranza['ldepositoencuentaconjunta']:
        output["Deposito"] = 'Cuenta del cliente'
    else:
        output["Deposito"] = cobranza['cxcuentadeposito__cxbanco__ctbanco'] \
            + ' Cta # ' + cobranza['cxcuentadeposito__cxcuenta']  
    output["Cobranza"] = cobranza['cxcobranza']
    output["Sobrepago"] = cobranza['nsobrepago']

    return output

@login_required(login_url='/login/')
@permission_required('contabilidad.add_diario_cabecera', login_url='bases:sin_permisos')
def GenerarAsientosCobranzas(request,ids):
    resultado=enviarPost("CALL uspGenerarAsientosCobranzas( '{0}',{1},'')"
        .format(ids, request.user.id, ))

    if resultado[0] !='OK':
        return HttpResponse(resultado)
    return HttpResponse('OK')

@login_required(login_url='/login/')
@permission_required('contabilidad.change_saldos', login_url='bases:sin_permisos')
def CierreDeMes(request, año, mes):
    nusuario = request.user.id
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    resultado=enviarPost("CALL uspBloqueoMesContabilidad( '{0}',{1},{2},{3},'')"
        .format(año, mes, nusuario, id_empresa.empresa.id))
    
    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('contabilidad.add_factura_venta', login_url='bases:sin_permisos')
def generaFacturasAlVencimiento(request):
    # la base de capital es el saldo del documento, el tiempo esde desde la fecha 
    # de negociación.

    template_name = 'contabilidad/datosgenerarfacturasalvencimiento_form.html'
    formulario={}
    # desembolso ={}

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    sp = Asignacion.objects.filter(cxestado='P'
                                   , leliminado=False
                                   , empresa = id_empresa.empresa).count()
    if request.method=='GET':

        e = {
            'cxnumerofactura':'...',
            # 'demision': desembolso,
        }

        concepto= 'SERVICIOS ENTREGADOS A {{cliente}} POR LA OPERACIÓN {{operacion}} DOCUMENTO {{documento}}'

        formulario = FacturaVentaForm(e, empresa = id_empresa.empresa)

        tipos_factoring = Tipos_factoring.objects\
            .filter(empresa = id_empresa.empresa
                    , leliminado = False
                    , lgenerafacturaenaceptacion = False)

        contexto={'solicitudes_pendientes':sp
                , 'form': formulario
                , 'concepto':concepto
                , 'tipo_factoring': tipos_factoring
                , 'ambiente': id_empresa.empresa.ambientesri
                }    
    
    return render(request, template_name, contexto)

def GeneraFacturasAlVencimientoDiario(request):
    # ejecuta un store procedure 
    pslocalidad = ''
    nusuario = request.user.id
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    objeto=json.loads(request.body.decode("utf-8"))
    pid_puntoemision =objeto["id_puntoemision"]
    psconcepto = objeto["concepto"]
    pdemision  = objeto["emision"]
    id_factoring  = objeto["id_factoring"]
    pdemision  = objeto["emision"]
    pnmes  = objeto["mes"]
    psaño  = objeto["año"]

    resultado=enviarPost("CALL uspGenerarFacturasAlVencimientoSinCargoDescontado( \
                         {0},{1},{2},'{3}'\
                         ,'{4}', {5},{6}, {7},'','')"
        .format(id_empresa.empresa.id, pid_puntoemision, id_factoring, psconcepto
                , pdemision, nusuario, pnmes, psaño))
       
    return HttpResponse(resultado)

def GeneraListaFacturasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        movimiento = Factura_venta.objects\
            .filter(empresa = id_empresa.empresa)\
            .order_by('dregistro')
        
    else:
        # la fecha de registro es datetime por lo que la comparación "hasta" es mejor
        # que sea con el día siguiente
        hasta = parse_date(hasta)
        hasta = hasta + timedelta(days=1)

        movimiento = Factura_venta.objects\
            .filter(demision__gte = desde
                    , empresa = id_empresa.empresa
                    , demision__lt = hasta)\
            .order_by('demision')
                
    tempBlogs = []
    for i in range(len(movimiento)):
        tempBlogs.append(GeneraListaFacturasJSONSalida(movimiento[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": movimiento.count(),
        "totalNotFiltered": movimiento.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaFacturasJSONSalida(transaccion):
    output = {}
    op = None

    output['id'] = transaccion.id
    output["Cliente"] = transaccion.cliente.cxcliente.ctnombre
    output["Registro"] = transaccion.dregistro.strftime("%Y-%m-%d")
    output["Emision"] = transaccion.demision.strftime("%Y-%m-%d")
    output["Valor"] =  transaccion.nvalor
    output["Saldo"] = transaccion.nsaldo
    output["Factura"] = transaccion.__str__()
    output["BaseIVA"] = transaccion.nbaseiva
    output["BaseNoIVA"] = transaccion.nbasenoiva
    output["IVA"] = transaccion.niva
    output["Origen"] = transaccion.cxtipooperacion
    id_origen = transaccion.operacion
    if transaccion.cxtipooperacion =='LC':
        op = Liquidacion_cabecera.objects.filter(pk = id_origen).first()
    elif transaccion.cxtipooperacion =='LA':
        op = Operacion.objects.filter(pk = id_origen).first()
    elif transaccion.cxtipooperacion == 'AP':
        op = Ampliaciones_plazo_cabecera.objects.filter(pk = id_origen).first()
    elif transaccion.cxtipooperacion == 'VF':
        op = Operacion.objects.filter(pk = id_origen).first()
    elif transaccion.cxtipooperacion == 'CP':
        op = Factura_cuota.objects.filter(pk = id_origen).first()
    if op:
        output["Operacion"] = op.__str__()
    output["Asiento"] = transaccion.asiento.cxtransaccion
    output["IdAsiento"] = transaccion.asiento.id
    return output

def GeneraListaProtestosJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        cobranzas = Cheques_protestados.objects\
            .filter(lcontabilizada = False, leliminado = False
                    ,empresa = id_empresa.empresa).order_by('dprotesto')
    else:
        cobranzas = Cheques_protestados.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , dprotesto__gte = desde, dprotesto__lte = hasta
                    , empresa = id_empresa.empresa)\
            .order_by('dprotesto')
        
    tempBlogs = []
    for i in range(len(cobranzas)):
        tempBlogs.append(GeneraListaProtestosJSONSalida(cobranzas[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": cobranzas.count(),
        "totalNotFiltered": cobranzas.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaProtestosJSONSalida(doc):
    output = {}

    output["id"] = doc.id
    output["Fecha"] = doc.dprotesto.strftime("%Y-%m-%d")
    output["Valor"] = doc.nvalor
    if doc.cxtipooperacion=='C':
        cobranza = Cobranzas.objects\
            .filter(cxcheque = doc.cheque).first()
        output["Cobranza"] = cobranza.cxcobranza
    else:
        cobranza = Recuperaciones_cabecera.objects\
            .filter(cxcheque = doc.cheque).first()
        output["Cobranza"] = cobranza.cxrecuperacion

    output["Cliente"] = cobranza.cxcliente.cxcliente.__str__()
    output["TipoFactoring"] = cobranza.cxtipofactoring.__str__()
    if cobranza.ldepositoencuentaconjunta:
        output["Deposito"] = 'Cuenta del cliente'
    else:
        output["Deposito"] = cobranza.cxcuentadeposito.__str__()
    output["sobrepago"] = cobranza.nsobrepago

    return output

@login_required(login_url='/login/')
@permission_required('contabilidad.add_diario_cabecera', login_url='bases:sin_permisos')
def GenerarAsientosProtestos(request,ids):
    resultado=enviarPost("CALL uspGenerarAsientosProtestos( '{0}',{1},'')"
        .format(ids, request.user.id, ))

    if resultado[0] !='OK':
        return HttpResponse(resultado)
    return HttpResponse('OK')

def GeneraListaTransferenciasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        cobranzas = Transferencias.objects\
            .filter(lcontabilizado = False, leliminado = False
                    ,empresa = id_empresa.empresa).order_by('dprotesto')
    else:
        cobranzas = Transferencias.objects\
            .filter(lcontabilizado = False, leliminado = False
                    , dmovimiento__gte = desde, dmovimiento__lte = hasta
                    , empresa = id_empresa.empresa)\
            .order_by('dmovimiento')
        
    tempBlogs = []
    for i in range(len(cobranzas)):
        tempBlogs.append(GeneraListaTransferenciasJSONSalida(cobranzas[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": cobranzas.count(),
        "totalNotFiltered": cobranzas.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaTransferenciasJSONSalida(doc):
    output = {}

    output["id"] = doc.id
    output["Fecha"] = doc.dmovimiento.strftime("%Y-%m-%d")
    output["Valor"] = doc.nvalor
    output["Cliente"] = doc.cuentaorigen.cxcliente.cxcliente.__str__()
    output["CuentaOrigen"] = doc.cuentaorigen.__str__()
    output["CuentaDestino"] = doc.cuentadestino.__str__()

    return output

@login_required(login_url='/login/')
@permission_required('contabilidad.add_diario_cabecera', login_url='bases:sin_permisos')
def GenerarAsientosTransferencias(request,ids):
    resultado=enviarPost("CALL uspGenerarAsientosTransferencias( '{0}',{1},'')"
        .format(ids, request.user.id, ))

    if resultado[0] !='OK':
        return HttpResponse(resultado)
    return HttpResponse('OK')

def GeneraListaRecuperacionesJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if desde == 'None':
        cobranzas = Recuperaciones_cabecera.objects\
            .filter(lcontabilizada = False, leliminado = False
                    ,empresa = id_empresa.empresa).order_by('dcobranza')
    else:
        cobranzas = Recuperaciones_cabecera.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , dcobranza__gte = desde, dcobranza__lte = hasta
                    , empresa = id_empresa.empresa)\
            .order_by('dcobranza')
        
    tempBlogs = []
    print(cobranzas)
    for i in range(len(cobranzas)):
        tempBlogs.append(GeneraListaRecuperacionesJSONSalida(cobranzas[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": cobranzas.count(),
        "totalNotFiltered": cobranzas.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaRecuperacionesJSONSalida(cobranza):
    output = {}

    output["id"] = cobranza.id
    output["Fecha"] = cobranza.dcobranza.strftime("%Y-%m-%d")
    output["Cliente"] = cobranza.cxcliente.cxcliente.ctnombre
    output["Valor"] = cobranza.nvalor
    output["TipoFactoring"] = cobranza.cxtipofactoring.ctabreviacion
    if cobranza.ldepositoencuentaconjunta:
        output["Deposito"] = 'Cuenta del cliente'
    else:
        output["Deposito"] = cobranza.cxcuentadeposito.__str__()
    output["Cobranza"] = cobranza.cxrecuperacion
    output["Sobrepago"] = cobranza.nsobrepago

    return output

@login_required(login_url='/login/')
@permission_required('contabilidad.add_diario_cabecera', login_url='bases:sin_permisos')
def GenerarAsientosRecuperaciones(request,ids):
    resultado=enviarPost("CALL uspGenerarAsientosRecuperaciones( '{0}',{1},'')"
        .format(ids, request.user.id, ))

    if resultado[0] !='OK':
        return HttpResponse(resultado)
    return HttpResponse('OK')

@login_required(login_url='/login/')
@permission_required('contabilidad.change_saldos', login_url='bases:sin_permisos')
def DesbloqueoDeMes(request, año, mes):
    nusuario = request.user.id
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    resultado=enviarPost("CALL uspDesbloqueoMesContabilidad( '{0}',{1},{2},{3},'')"
        .format(año, mes, nusuario, id_empresa.empresa.id))
    
    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('contabilidad.view_cuentas_especiales', login_url='bases:sin_permisos')
def BuscarCuentasReestructuracion(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    pk = Cuentas_reestructuracion.objects.filter(empresa = id_empresa.empresa).first()
    if pk:
        return redirect("contabilidad:asignarcuentascontablesreestructuracion_editar", pk=pk.id)
    else:
        return redirect("contabilidad:asignarcuentascontablesreestructuracion_nueva")


def CargarDetalleAsiento(request, diario_id):
    # cargar el detalle del asiento contable
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    detalle_asiento = Transaccion.objects\
        .filter(diario = diario_id, leliminado = False
                , empresa = id_empresa.empresa)\
        .order_by('cxcuenta')
    
    data = list(detalle_asiento\
                .values('cxcuenta'
                        , 'cxtipo', 'ctreferencia'
                        , 'nvalor', 'id')
                .annotate(
                    cxcuenta__ctcuenta = Concat( F('cxcuenta__cxcuenta')
                                    , Value(' ')
                                    ,F('cxcuenta__ctcuenta')
                                    ,output_field=CharField() )
                        )
            )

    return JsonResponse(data, safe=False)