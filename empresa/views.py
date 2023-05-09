from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy

from .models import Tipos_factoring, Tasas_factoring, Clases_cliente\
    , Cuentas_bancarias, Localidades
from bases.models import Usuario_empresa

from .forms import CuentaBancariaForm, TipoFactoringForm, TasaFactoringForm\
    , ClasesParticipantesForm, LocalidadForm


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


