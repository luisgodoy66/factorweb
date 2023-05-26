from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q, FilteredRelation

from .models import Plan_cuentas, Cuentas_especiales, Cuentas_bancos\
    , Cuentas_tiposfactoring, Cuentas_tasasfactoring
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from empresa.models import Cuentas_bancarias, Tipos_factoring, Tasas_factoring

from .forms import CuentasEspecialesForm, CuentasBancosForm\
    , CuentasTiposFactoringForm, CuentasTasaTiposFactoringForm

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

def BuscarCuentasEspeciales(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    pk = Cuentas_especiales.objects.filter(empresa = id_empresa.empresa).first()
    if pk:
        return redirect("contabilidad:asignarcuentascontables_editar", pk=pk.id)
    else:
        return redirect("contabilidad:asignarcuentascontables_nueva")
    
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
            .filter(empresa=id_empresa.empresa, cuenta_tasatipofactoring__tasafactoring = id_tasa)\
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
