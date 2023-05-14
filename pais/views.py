from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy

from .models import Bancos, Feriados
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion

from .forms import BancoForm, FeriadoForm

class BancosView(LoginRequiredMixin, generic.ListView):
    model = Bancos
    template_name = "pais/listabancos.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Bancos.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        context = super(BancosView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class BancosNew(LoginRequiredMixin, generic.CreateView):
    model = Bancos
    template_name="pais/datosbanco_form.html"
    form_class=BancoForm
    context_object_name='banco'
    success_url= reverse_lazy("pais:listabancos")
    login_url = 'bases:login'

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BancosNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class BancosEdit(LoginRequiredMixin, generic.UpdateView):
    model = Bancos
    template_name="pais/datosbanco_form.html"
    context_object_name = "banco"
    form_class=BancoForm
    success_url=reverse_lazy("pais:listabancos")
    success_message="Banco actualizado satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BancosEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class FeriadosView(LoginRequiredMixin, generic.ListView):
    model = Feriados
    template_name = "pais/listaferiados.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Feriados.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs

    def get_context_data(self, **kwargs):
        context = super(FeriadosView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class FeriadosNew(LoginRequiredMixin, generic.CreateView):
    model = Feriados
    template_name="pais/datosferiado_form.html"
    form_class=FeriadoForm
    context_object_name='feriado'
    success_url= reverse_lazy("pais:listaferiados")
    login_url = 'bases:login'

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FeriadosNew, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class FeriadosEdit(LoginRequiredMixin, generic.UpdateView):
    model = Feriados
    template_name="pais/datosferiado_form.html"
    form_class=FeriadoForm
    context_object_name='feriado'
    success_url= reverse_lazy("pais:listaferiados")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FeriadosEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context
