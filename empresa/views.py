from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
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

from bases.views import enviarPost, SinPrivilegios

class TiposFactoringView(SinPrivilegios, generic.ListView):
    model = Tipos_factoring
    template_name = "empresa/listatiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="empresa.view_tipos_factoring"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tipos_factoring.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("cttipofactoring")
        return qs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(TiposFactoringView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class TipoFactoringNew(SinPrivilegios, generic.CreateView):
    model = Tipos_factoring
    template_name="empresa/datostipofactoring_form.html"
    form_class=TipoFactoringForm
    context_object_name='tipofactoring'
    success_url= reverse_lazy("empresa:listatiposfactoring")
    login_url = 'bases:login'
    permission_required="empresa.add_tipos_factoring"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        # marcar como tipo de factoring creado
        empresa = Empresas.objects.filter (pk = id_empresa.empresa.id).first()
        empresa.ltipofactoringconfigurado = True
        empresa.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(TipoFactoringNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_success_url(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        empresa = Empresas.objects.filter (pk = id_empresa.empresa.id).first()
        if not empresa.ltasasfactoringconfiguradas :
            return reverse_lazy("bases:home")
        if not empresa.ltipofactoringconfigurado :
            return reverse_lazy("bases:home")

        return reverse_lazy("empresa:listatiposfactoring")
    
class TipoFactoringEdit(SinPrivilegios, generic.UpdateView):
    model = Tipos_factoring
    template_name="empresa/datostipofactoring_form.html"
    form_class=TipoFactoringForm
    context_object_name='tipofactoring'
    success_url= reverse_lazy("empresa:listatiposfactoring")
    login_url = 'bases:login'
    permission_required="empresa.change_tipos_factoring"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(TipoFactoringEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class TasasFactoringView(SinPrivilegios, generic.ListView):
    model = Tasas_factoring
    template_name = "empresa/listatasasfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="empresa.view_tasas_factoring"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Tasas_factoring.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("cttasa")
        return qs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(TasasFactoringView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class TasaFactoringNew(SinPrivilegios, generic.CreateView):
    model = Tasas_factoring
    template_name="empresa/datostasafactoring_form.html"
    form_class=TasaFactoringForm
    context_object_name='tasafactoring'
    success_url= reverse_lazy("empresa:listatasasfactoring")
    login_url = 'bases:login'
    permission_required="empresa.add_tasas_factoring"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.cxusuariocrea = self.request.user
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(TasaFactoringNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class TasaFactoringEdit(SinPrivilegios, generic.UpdateView):
    model = Tasas_factoring
    template_name="empresa/datostasafactoring_form.html"
    form_class=TasaFactoringForm
    context_object_name='tasafactoring'
    success_url= reverse_lazy("empresa:listatasasfactoring")
    login_url = 'bases:login'
    permission_required="empresa.change_tasas_factoring"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        # marcar como tipo de factoring creado
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        empresa = Empresas.objects.filter (pk = id_empresa.empresa.id).first()
        empresa.ltasasfactoringconfiguradas = True
        empresa.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(TasaFactoringEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_success_url(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        empresa = Empresas.objects.filter (pk = id_empresa.empresa.id).first()
        if not empresa.ltasasfactoringconfiguradas :
            return reverse_lazy("bases:home")
        if not empresa.ltipofactoringconfigurado :
            return reverse_lazy("bases:home")

        return reverse_lazy("empresa:listatasasfactoring")

class ClasesParticipanteView(SinPrivilegios, generic.ListView):
    model = Clases_cliente
    template_name = "empresa/listaclasesparticipantes.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="empresa.view_clases_cliente"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Clases_cliente.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("cxclase")
        return qs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ClasesParticipanteView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class ClasesParticipanteNew(SinPrivilegios, generic.CreateView):
    model = Clases_cliente
    template_name="empresa/datosclaseparticipante_form.html"
    form_class=ClasesParticipantesForm
    context_object_name='clase'
    success_url= reverse_lazy("empresa:listaclasesparticipantes")
    login_url = 'bases:login'
    permission_required="empresa.add_clases_cliente"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.cxusuariocrea = self.request.user
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ClasesParticipanteNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasBancariasView(SinPrivilegios, generic.ListView):
    model = Cuentas_bancarias
    template_name = "empresa/listacuentasbancarias.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="empresa.view_cuentas_bancarias"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Cuentas_bancarias.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)
        return qs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentasBancariasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentaBancariaNew(SinPrivilegios, generic.CreateView):
    model = Cuentas_bancarias
    template_name="empresa/datoscuentabancaria_form.html"
    form_class=CuentaBancariaForm
    context_object_name='cuentabancaria'
    success_url= reverse_lazy("empresa:listacuentasbancarias")
    login_url = 'bases:login'
    permission_required="empresa.add_cuentas_bancarias"

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
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentaBancariaNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context
       
class CuentaBancariaEdit(SinPrivilegios, generic.UpdateView):
    model = Cuentas_bancarias
    template_name="empresa/datoscuentabancaria_form.html"
    form_class=CuentaBancariaForm
    context_object_name='cuentabancaria'
    success_url= reverse_lazy("empresa:listacuentasbancarias")
    login_url = 'bases:login'
    permission_required="empresa.change_cuentas_bancarias"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(CuentaBancariaEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(CuentaBancariaEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class LocalidadesView(SinPrivilegios, generic.ListView):
    model = Localidades
    template_name = "empresa/listalocalidades.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="empresa.view_localidades"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Localidades.objects.filter(leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("ctlocalidad")
        return qs
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(LocalidadesView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class LocalidadesNew(SinPrivilegios, generic.CreateView):
    model = Localidades
    template_name="empresa/datoslocalidad_form.html"
    form_class=LocalidadForm
    context_object_name='localidad'
    success_url= reverse_lazy("empresa:listalocalidades")
    login_url = 'bases:login'
    permission_required="empresa.add_localidades"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(LocalidadesNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class LocalidadesEdit(SinPrivilegios, generic.UpdateView):
    model = Localidades
    template_name="empresa/datoslocalidad_form.html"
    form_class=LocalidadForm
    context_object_name='localidad'
    success_url= reverse_lazy("empresa:listalocalidades")
    login_url = 'bases:login'
    permission_required="empresa.change_localidades"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(LocalidadesEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class PuntosEmisionView(SinPrivilegios, generic.ListView):
    model = Puntos_emision
    template_name="empresa/listapuntosemision.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="empresa.view_puntos_emision"

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

class PuntoEmisionNew(SinPrivilegios, generic.CreateView):
    model = Puntos_emision
    template_name="empresa/datospuntoemision_form.html"
    form_class=PuntoEmisionForm
    context_object_name='puntoemision'
    success_url= reverse_lazy("empresa:listapuntosemision")
    login_url = 'bases:login'
    permission_required="empresa.add_puntos_emision"

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

class PuntoEmisionEdit(SinPrivilegios, generic.UpdateView):
    model = Puntos_emision
    template_name="empresa/datospuntoemision_form.html"
    form_class=PuntoEmisionForm
    context_object_name='puntoemision'
    success_url= reverse_lazy("empresa:listapuntosemision")
    login_url = 'bases:login'
    permission_required="empresa.change_puntos_emision"

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

class DatosEmpresaEdit(SinPrivilegios, generic.UpdateView):
    model = Empresas
    template_name="empresa/datosempresa_form.html"
    form_class=EmpresaForm
    context_object_name='empresa'
    success_url= reverse_lazy("bases:home")
    login_url = 'bases:login'
    permission_required="empresa.change_empresas"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(DatosEmpresaEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context
