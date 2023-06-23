from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q, FilteredRelation, F
from django.db.models.expressions import RawSQL 
from django.http import JsonResponse
import json

from .models import Plan_cuentas, Cuentas_especiales, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring, Factura_venta\
    , Cuentas_diferidos, Cuentas_provisiones
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from empresa.models import Cuentas_bancarias, Tipos_factoring, Puntos_emision\
    , Contador, Tasas_factoring
from operaciones.models import Asignacion as Operacion, Movimientos_maestro
from cobranzas.models import Liquidacion_cabecera
from operaciones.models import Ampliaciones_plazo_cabecera, Desembolsos

from bases.views import enviarPost

from .forms import CuentasEspecialesForm, CuentasBancosForm, FacturaVentaForm\
    , CuentasTiposFactoringForm, CuentasTasaTiposFactoringForm\
    , ComprobanteEgresoForm, CuentasDiferidoTasaTiposFactoringForm\
    , CuentasProvisionTasaTiposFactoringForm, PlanCuentasForm

import xml.etree.cElementTree as etree

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
            'demision': desembolso.dregistro,
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

    if not pid_factura == 'NONE':
        pid_factura = 'NULL'

    print(pid_cuentapago)
    resultado=enviarPost("CALL uspGenerarEgresoContabilidad( '{0}',{1},'{2}','{3}'\
                         ,{4},'{5}',{6},'{7}','{8}'\
                         ,{9},{10},{11},'',0)"
        .format(psforma_pago, pid_desembolso, pscxbeneficiario, psrecibidopor\
                , pid_cuentapago, pscheque, pid_cuentadestino, psconcepto, pdemision\
            ,pnvalor, pid_factura, nusuario))
    return HttpResponse(resultado)
