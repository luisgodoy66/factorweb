from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q, FilteredRelation, Max
from django.db.models.functions import Concat
from django.db.models.expressions import RawSQL 
from django.http import JsonResponse
from django.db import transaction
from django.views import generic

import json

from .models import Plan_cuentas, Cuentas_especiales, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring, Factura_venta\
    , Cuentas_diferidos, Cuentas_provisiones, Diario_cabecera, Transaccion\
    , Comprobante_egreso, Control_meses
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from empresa.models import Cuentas_bancarias, Tipos_factoring, Puntos_emision\
    , Contador, Tasas_factoring
from operaciones.models import Asignacion as Operacion, Movimientos_maestro\
    , Ampliaciones_plazo_cabecera, Desembolsos
from cobranzas.models import Liquidacion_cabecera, Documentos_cabecera as Cobranzas

from bases.views import enviarPost, enviarConsulta

from .forms import CuentasEspecialesForm, CuentasBancosForm, FacturaVentaForm\
    , CuentasTiposFactoringForm, CuentasTasaTiposFactoringForm\
    , ComprobanteEgresoForm, CuentasDiferidoTasaTiposFactoringForm\
    , CuentasProvisionTasaTiposFactoringForm, PlanCuentasForm, DiarioCabeceraForm\
    , TransaccionForm

import xml.etree.cElementTree as etree
from datetime import date, timedelta, datetime

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

class CuentasNew(LoginRequiredMixin, generic.CreateView):
    model = Plan_cuentas
    template_name = "contabilidad/datoscuenta_form.html"
    context_object_name='cuentas'
    form_class = PlanCuentasForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CuentasNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P',leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasEdit(LoginRequiredMixin, generic.UpdateView):
    model = Plan_cuentas
    template_name = "contabilidad/datoscuenta_form.html"
    context_object_name='cuentas'
    form_class = PlanCuentasForm
    success_url= reverse_lazy("contabilidad:listacuentascontables")
    login_url = 'bases:login'

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CuentasEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P',leliminado=False).count()
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
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentastasasfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , litemfactura = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context = super(CuentasTasasFactoringView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasDiferidosView(LoginRequiredMixin, generic.ListView):
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentastasasfactoring2.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , litemfactura = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context = super(CuentasDiferidosView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp

        return context

class CuentasProvisionesView(LoginRequiredMixin, generic.ListView):
    model = Movimientos_maestro
    template_name = "contabilidad/listacuentastasasfactoring3.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Movimientos_maestro.objects\
            .filter(leliminado = False
                    , litemfactura = True
                    , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context = super(CuentasProvisionesView, self).get_context_data(**kwargs)
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
    
class CuentasTasaDiferidoView(LoginRequiredMixin, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastasadiferido.html"
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
        context = super(CuentasTasaDiferidoView, self).get_context_data(**kwargs)
        context["solicitudes_pendientes"]=sp
        context["id_tasa"]=id_tasa
        context["nombre_tasa"]=nombre_tasa

        return context
    
class CuentasTasaProvisionView(LoginRequiredMixin, generic.ListView):
    model = Tipos_factoring
    template_name = "contabilidad/listacuentastasaprovision.html"
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
        context = super(CuentasTasaProvisionView, self).get_context_data(**kwargs)
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

class CuentaDiferidoTasaTipoFactoringNew(LoginRequiredMixin, generic.CreateView):
    model=Cuentas_diferidos
    template_name="contabilidad/datoscuentadiferidotasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasDiferidoTasaTiposFactoringForm
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

class CuentaProvisionTasaTipoFactoringNew(LoginRequiredMixin, generic.CreateView):
    model=Cuentas_provisiones
    template_name="contabilidad/datoscuentaprovisiontasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasProvisionTasaTiposFactoringForm
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

class CuentaDiferidoTasaTipoFactoringEdit(LoginRequiredMixin, generic.UpdateView):
    model=Cuentas_diferidos
    template_name="contabilidad/datoscuentadiferidotasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasDiferidoTasaTiposFactoringForm
    # success_url=reverse_lazy("contabilidad:listacuentastasatiposfactoring")
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

class CuentaProvisionTasaTipoFactoringEdit(LoginRequiredMixin, generic.UpdateView):
    model=Cuentas_provisiones
    template_name="contabilidad/datoscuentaprovisiontasatipofactoring_modal.html"
    context_object_name = "consulta"
    form_class=CuentasProvisionTasaTiposFactoringForm
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

class PendientesGenerarFacturaView(LoginRequiredMixin, generic.ListView):
    model = Plan_cuentas
    template_name = "contabilidad/listapendientesgenerarfactura.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        asgn=Operacion.objects\
            .filter(leliminado = False, empresa = id_empresa.empresa
                    , lfacturagenerada = False
                    , cxtipofactoring__lgenerafacturaenaceptacion = True)\
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
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class AsientosView(LoginRequiredMixin, generic.ListView):
    model = Diario_cabecera
    template_name = "contabilidad/listaasientoscontables.html"
    context_object_name='consulta'
    login_url = 'bases:login'

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
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class DiariosConsulta(LoginRequiredMixin, generic.TemplateView):
    # model = Diario_cabecera
    template_name = "contabilidad/consultageneralasientos.html"
    # context_object_name='consulta'
    login_url = 'bases:login'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(DiariosConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context
 
class LibroMayorConsulta(LoginRequiredMixin, generic.TemplateView):
    # model = Asignacion
    template_name = "contabilidad/consultalibromayor.html"
    # context_object_name='consulta'
    # login_url = 'bases:login'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(LibroMayorConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] =hasta
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        context['cuentas'] = Plan_cuentas.objects\
            .filter(empresa= id_empresa.empresa, nnivel__gte= 4, leliminado= False)\
            .order_by('cxcuenta')
        return context

class ListaCobranzasAGenerar(LoginRequiredMixin, generic.TemplateView):
    # model = Diario_cabecera
    template_name = "contabilidad/listacobranzaspendientescontabilizar.html"
    # context_object_name='consulta'
    login_url = 'bases:login'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # obtener primer día del mes actual
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()

        context = super(ListaCobranzasAGenerar, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] = hasta
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context
 
class BalanceGeneralConsulta(LoginRequiredMixin, generic.TemplateView):
    # model = Asignacion
    template_name = "contabilidad/consultabalancegeneral.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()

        mescerrado = Control_meses.objects.filter(lbloqueado = True, empresa = id_empresa.empresa)\
            .values('empresa')\
            .annotate(ultimomes = Max(Concat('año','mes'))).first()
        
        if mescerrado:
            añomes = mescerrado['ultimomes']
            año = añomes[0:4]
            mes = int(añomes[4:6])
            if mes < 12:
                mes +=1
        else:
            año = datetime.now().year
            mes = datetime.now().month


        context = super(BalanceGeneralConsulta, self).get_context_data(**kwargs)
        context['solicitudes_pendientes'] = sp
        context['año'] = año
        context['mes'] = mes

        return context

class PerdiasyGananciasConsulta(LoginRequiredMixin, generic.TemplateView):
    # model = Asignacion
    template_name = "contabilidad/consultaperdidasyganancias.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()

        mescerrado = Control_meses.objects.filter(lbloqueado = True, empresa = id_empresa.empresa)\
            .values('empresa')\
            .annotate(ultimomes = Max(Concat('año','mes'))).first()
        
        if mescerrado:
            añomes = mescerrado['ultimomes']
            año = añomes[0:4]
            mes = int(añomes[4:6])
            if mes < 12:
                mes +=1
        else:
            año = datetime.now().year
            mes = datetime.now().month

        context = super(PerdiasyGananciasConsulta, self).get_context_data(**kwargs)
        context['solicitudes_pendientes'] = sp
        context['año'] = año
        context['mes'] = mes

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

    gaoa = Tasas_factoring.objects.filter(cxtasa="GAOA"
                                         , empresa = id_empresa.empresa).first()
    if not gaoa:
        return HttpResponse("no encontró registro de tasa de gao adicional en tabla de tasas de factoring")

    if tipo == 'LA':
        documento_origen = Operacion.objects.get(id=pk)
        valor_gao = documento_origen.ngao
        valor_dc = documento_origen.ndescuentodecartera
        valor_iva=documento_origen.niva
        desembolso=documento_origen.ddesembolso

    if tipo == 'LC':
        documento_origen = Liquidacion_cabecera.objects.get(id=pk)
        valor_gao = documento_origen.ngao
        valor_dc = documento_origen.ndescuentodecartera
        valor_dcv = documento_origen.ndescuentodecarteravencido
        valor_gaoa = documento_origen.ngaoa
        valor_iva=documento_origen.niva
        desembolso=documento_origen.ddesembolso

    if tipo == 'AP':
        documento_origen = Ampliaciones_plazo_cabecera.objects.get(id=pk)
        valor_gaoa = documento_origen.ncomision
        valor_dcv = documento_origen.ndescuentodecartera
        valor_iva=documento_origen.niva
        desembolso=documento_origen.notadebito.dnotadebito

    id_operacion=documento_origen.id    
    id_cliente=documento_origen.cxcliente
    cliente = documento_origen.cxcliente.cxcliente.ctnombre
    porc_iva=documento_origen.nporcentajeiva

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

    if request.method=='GET':

        e = {
            'cxnumerofactura':'...',
            'demision': desembolso,
            'cxestado':'A',
            'niva' : valor_iva,
            'nvalor':valor_gao + valor_dc + valor_dcv + valor_gaoa + valor_iva,
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

        formulario = ComprobanteEgresoForm(e, empresa = id_empresa.empresa)

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

    resultado=enviarPost("CALL uspGenerarFacturaContabilidad( '{0}',{1},{2},{3}\
                         ,{4},{5},{6},'{7}',{8}\
                         ,{9},{10},{11},'{12}'\
                         ,{13},{14},'',0)"
        .format(pstipo_operacion,pid_operacion,pid_puntoemision,pid_cliente\
                , pnbase_iva, pnbase_noiva, pniva, psconcepto, pngao\
            ,pndescuentocartera, pngaoa, pndescuentocarteravencido, pdemision
            , porcentaje_iva, nusuario))
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

    resultado=enviarPost("CALL uspGenerarEgresoContabilidad( '{0}',{1},'{2}','{3}'\
                         ,{4},'{5}',{6},'{7}','{8}'\
                         ,{9},{10},{11},'',0)"
        .format(psforma_pago, pid_desembolso, pscxbeneficiario, psrecibidopor\
                , pid_cuentapago, pscheque, pid_cuentadestino, psconcepto, pdemision\
            ,pnvalor, pid_factura, nusuario))
    return HttpResponse(resultado)

def DatosDiarioContable(request, diario_id=None):
    template_name="solicitudes/datosasiento_form.html"
    formulario = {}
    diario = {}
    
    if request.method=='GET':

        diario = Diario_cabecera.objects.filter(pk=diario_id).first()

        if diario:
            e={
                'cxtransaccion': diario.cxtransaccion,
                'ctconcepto': diario.ctconcepto,
                'nvalor': diario.nvalor,
                'dcontabilizado':diario.dcontabilizado
            }
            formulario = DiarioCabeceraForm(e)
        else:
            formulario=DiarioCabeceraForm()
            diario=None
            
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()

    contexto={'form_diario':formulario,
        'diario' : diario,
        'diario_id': diario_id,
        'solicitudes_pendientes':sp
       }


    return render(request, template_name, contexto)

def AsientoDiarioNuevo(request, diario_id = None):

    template_name="contabilidad/datosasiento_form.html"
    
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False).count()

    contexto={'form_diario': DiarioCabeceraForm(),
            'solicitudes_pendientes':sp
       }
    
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
                sec.nultimonumero +=1
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
                return redirect("contabilidad:listaasientocontables")

            # grabar detalle 

            # recuperar el string de lista  pasado en la data y
            # convertir a lista
            lista = request.POST.get("Diario")
            output = eval(lista)

            for elem in output:      
                #accedemos a cada elemento de la lista (en este caso cada elemento es un dictionario)
                cuenta = Plan_cuentas.objects.filter(id = elem.get("cuenta")).first()

                if elem.get("tipo") =='D':
                    nvalor = elem.get("debe")
                else:
                    nvalor = elem.get("haber")

                detalle = Transaccion(
                    diario = diario,
                    cxcuenta=cuenta,
                    cxtipo = elem.get("tipo"),
                    nvalor = nvalor,
                    ctreferencia = elem.get("referencia"),
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if detalle:
                    detalle.save()
            


        # la ejecucion de esta vista POST se hace por jquery.ajax 
        # y ese proceso imprime el asiento y devuelve a la lista de asientos
        return HttpResponse( diario_id)
    
    return render(request, template_name, contexto)

def DatosDiarioEditar(request, detalle_id = None):

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
              'detalle': detalle_id,
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
        cobranzas = Cobranzas.objects\
            .filter(lcontabilizada = False, leliminado = False
                    ,empresa = id_empresa.empresa).order_by('dcobranza')
    else:
        cobranzas = Cobranzas.objects\
            .filter(lcontabilizada = False, leliminado = False
                    , dcobranza__gte = desde, dcobranza__lte = hasta
                    , empresa = id_empresa.empresa)\
            .order_by('dcobranza')
        
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

    output["id"] = cobranza.id
    output["Fecha"] = cobranza.dcobranza.strftime("%Y-%m-%d")
    output["Cliente"] = cobranza.cxcliente.cxcliente.ctnombre
    output["Valor"] = cobranza.nvalor
    output["TipoFactoring"] = cobranza.cxtipofactoring.ctabreviacion
    if cobranza.ldepositoencuentaconjunta:
        output["Deposito"] = 'Cuenta del cliente'
    else:
        output["Deposito"] = cobranza.cxcuentadeposito.__str__()
    output["sobrepago"] = cobranza.nsobrepago

    return output

def GenerarAsientosCobranzas(request,ids):
    resultado=enviarPost("CALL uspGenerarAsientosCobranzas( '{0}',{1},'')"
        .format(ids, request.user.id, ))

    if resultado[0] !='OK':
        return HttpResponse(resultado)

    return redirect("contabilidad:listacobranzaspendientescontabilizar")
