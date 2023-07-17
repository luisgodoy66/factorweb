from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy

from .models import Tipos_factoring, Tasas_factoring, Clases_cliente\
    , Cuentas_bancarias, Localidades, Puntos_emision
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from bases.models import Empresas

from .forms import CuentaBancariaForm, TipoFactoringForm, TasaFactoringForm\
    , ClasesParticipantesForm, LocalidadForm, PuntoEmisionForm
from bases.forms import EmpresaForm

class TiposFactoringView(LoginRequiredMixin, generic.ListView):
    model = Tipos_factoring
    template_name = "empresa/listatiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tipos_factoring.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("cttipofactoring")
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(TiposFactoringView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class TipoFactoringNew(LoginRequiredMixin, generic.CreateView):
    model = Tipos_factoring
    template_name="empresa/datostipofactoring_form.html"
    form_class=TipoFactoringForm
    context_object_name='tipofactoring'
    success_url= reverse_lazy("empresa:listatiposfactoring")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(TipoFactoringNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class TipoFactoringEdit(LoginRequiredMixin, generic.UpdateView):
    model = Tipos_factoring
    template_name="empresa/datostipofactoring_form.html"
    form_class=TipoFactoringForm
    context_object_name='tipofactoring'
    success_url= reverse_lazy("empresa:listatiposfactoring")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(TipoFactoringEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class TasasFactoringView(LoginRequiredMixin, generic.ListView):
    model = Tasas_factoring
    template_name = "empresa/listatasasfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tasas_factoring.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("cttasa")
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(TasasFactoringView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class TasaFactoringNew(LoginRequiredMixin, generic.CreateView):
    model = Tasas_factoring
    template_name="empresa/datostasafactoring_form.html"
    form_class=TasaFactoringForm
    context_object_name='tasafactoring'
    success_url= reverse_lazy("empresa:listatasasfactoring")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(TasaFactoringNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class TasaFactoringEdit(LoginRequiredMixin, generic.UpdateView):
    model = Tasas_factoring
    template_name="empresa/datostasafactoring_form.html"
    form_class=TasaFactoringForm
    context_object_name='tasafactoring'
    success_url= reverse_lazy("empresa:listatasasfactoring")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(TasaFactoringEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class ClasesParticipanteView(LoginRequiredMixin, generic.ListView):
    model = Clases_cliente
    template_name = "empresa/listaclasesparticipantes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Clases_cliente.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("cxclase")
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(ClasesParticipanteView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class ClasesParticipanteNew(LoginRequiredMixin, generic.CreateView):
    model = Clases_cliente
    template_name="empresa/datosclaseparticipante_form.html"
    form_class=ClasesParticipantesForm
    context_object_name='clase'
    success_url= reverse_lazy("empresa:listaclasesparticipantes")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(ClasesParticipanteNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasBancariasView(LoginRequiredMixin, generic.ListView):
    model = Cuentas_bancarias
    template_name = "empresa/listacuentasbancarias.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Cuentas_bancarias.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(CuentasBancariasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentaBancariaNew(LoginRequiredMixin, generic.CreateView):
    model = Cuentas_bancarias
    template_name="empresa/datoscuentabancaria_form.html"
    form_class=CuentaBancariaForm
    context_object_name='cuentabancaria'
    success_url= reverse_lazy("empresa:listacuentasbancarias")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CuentaBancariaNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(CuentaBancariaNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context
       
class CuentaBancariaEdit(LoginRequiredMixin, generic.UpdateView):
    model = Cuentas_bancarias
    template_name="empresa/datoscuentabancaria_form.html"
    form_class=CuentaBancariaForm
    context_object_name='cuentabancaria'
    success_url= reverse_lazy("empresa:listacuentasbancarias")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(CuentaBancariaEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(CuentaBancariaEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class LocalidadesView(LoginRequiredMixin, generic.ListView):
    model = Localidades
    template_name = "empresa/listalocalidades.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Localidades.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("ctlocalidad")
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(LocalidadesView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class LocalidadesNew(LoginRequiredMixin, generic.CreateView):
    model = Localidades
    template_name="empresa/datoslocalidad_form.html"
    form_class=LocalidadForm
    context_object_name='localidad'
    success_url= reverse_lazy("empresa:listalocalidades")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(LocalidadesNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class LocalidadesEdit(LoginRequiredMixin, generic.UpdateView):
    model = Localidades
    template_name="empresa/datoslocalidad_form.html"
    form_class=LocalidadForm
    context_object_name='localidad'
    success_url= reverse_lazy("empresa:listalocalidades")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(LocalidadesEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class PuntosEmisionView(LoginRequiredMixin, generic.ListView):
    model = Puntos_emision
    template_name="empresa/listapuntosemision.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Puntos_emision.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(PuntosEmisionView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P'
                                       ,leliminado=False
                                       , empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class PuntoEmisionNew(LoginRequiredMixin, generic.CreateView):
    model = Puntos_emision
    template_name="empresa/datospuntoemision_form.html"
    form_class=PuntoEmisionForm
    context_object_name='puntoemision'
    success_url= reverse_lazy("empresa:listapuntosemision")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(PuntoEmisionNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P',leliminado=False
                                       , empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class PuntoEmisionEdit(LoginRequiredMixin, generic.UpdateView):
    model = Puntos_emision
    template_name="empresa/datospuntoemision_form.html"
    form_class=PuntoEmisionForm
    context_object_name='puntoemision'
    success_url= reverse_lazy("empresa:listapuntosemision")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(PuntoEmisionEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P',leliminado=False
                                       , empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class DatosEmpresaEdit(LoginRequiredMixin, generic.UpdateView):
    model = Empresas
    template_name="empresa/datosempresa_form.html"
    form_class=EmpresaForm
    context_object_name='empresa'
    success_url= reverse_lazy("bases:dashboard")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(DatosEmpresaEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context
