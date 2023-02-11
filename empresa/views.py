from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from .models import Tipos_factoring, Tasas_factoring, Clases_cliente\
    , Cuentas_bancarias, Localidades
from .forms import CuentaBancariaForm, TipoFactoringForm, TasaFactoringForm\
    , ClasesParticipantesForm, LocalidadForm


class TiposFactoringView(LoginRequiredMixin, generic.ListView):
    model = Tipos_factoring
    template_name = "empresa/listatiposfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class TipoFactoringNew(LoginRequiredMixin, generic.CreateView):
    model = Tipos_factoring
    template_name="empresa/datostipofactoring_form.html"
    form_class=TipoFactoringForm
    context_object_name='tipofactoring'
    success_url= reverse_lazy("empresa:listatiposfactoring")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
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

class TasaFactoringNew(LoginRequiredMixin, generic.CreateView):
    model = Tasas_factoring
    template_name="empresa/datostasafactoring_form.html"
    form_class=TasaFactoringForm
    context_object_name='tasafactoring'
    success_url= reverse_lazy("empresa:listatasasfactoring")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
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

class ClasesParticipanteNew(LoginRequiredMixin, generic.CreateView):
    model = Clases_cliente
    template_name="empresa/datosclaseparticipante_form.html"
    form_class=ClasesParticipantesForm
    context_object_name='clase'
    success_url= reverse_lazy("empresa:listaclasesparticipantes")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class CuentasBancariasView(LoginRequiredMixin, generic.ListView):
    model = Cuentas_bancarias
    template_name = "empresa/listacuentasbancarias.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class CuentaBancariaNew(LoginRequiredMixin, generic.CreateView):
    model = Cuentas_bancarias
    template_name="empresa/datoscuentabancaria_form.html"
    form_class=CuentaBancariaForm
    context_object_name='cuentabancaria'
    success_url= reverse_lazy("empresa:listacuentasbancarias")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class CuentaBancariaEdit(LoginRequiredMixin, generic.UpdateView):
    model = Cuentas_bancarias
    template_name="empresa/datoscuentabancaria_form.html"
    form_class=CuentaBancariaForm
    context_object_name='cuentabancaria'
    success_url= reverse_lazy("empresa:listacuentasbancarias")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user
        return super().form_valid(form)

class LocalidadesView(LoginRequiredMixin, generic.ListView):
    model = Localidades
    template_name = "empresa/listalocalidades.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class LocalidadesNew(LoginRequiredMixin, generic.CreateView):
    model = Localidades
    template_name="empresa/datoslocalidad_form.html"
    form_class=LocalidadForm
    context_object_name='localidad'
    success_url= reverse_lazy("empresa:listalocalidades")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
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


