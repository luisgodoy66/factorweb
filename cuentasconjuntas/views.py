from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
# from django.http import HttpResponse, JsonResponse
# from django.contrib.auth.decorators import login_required, permission_required
# from django.db import transaction
from django.urls import reverse_lazy
# from django.db.models import Count, Sum, Q
from django.db.models.expressions import RawSQL 

from .models import Cuentas_bancarias, Movimientos
from cobranzas.models import Documentos_cabecera, Recuperaciones_cabecera

from .forms import CuentasBancariasForm, DebitosForm, TransferenciasForm

class CuentasView(LoginRequiredMixin, generic.ListView):
    model = Cuentas_bancarias
    template_name = "cuentasconjuntas/listacuentasbancarias.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class CuentasBancariasNew(LoginRequiredMixin, generic.CreateView):
    model = Cuentas_bancarias
    template_name = "cuentasconjuntas/datoscuentabancaria_modal.html"
    context_object_name='cuentas'
    form_class = CuentasBancariasForm
    success_url= reverse_lazy("cuentasconjuntas:listadocuentasconjuntas")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CuentasBancariasNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        return context

class CuentasBancariasEdit(LoginRequiredMixin, generic.UpdateView):
    model = Cuentas_bancarias
    template_name = "cuentasconjuntas/datoscuentabancaria_modal.html"
    context_object_name='cuentas'
    form_class = CuentasBancariasForm
    success_url= reverse_lazy("cuentasconjuntas:listadocuentas")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')

        context = super(CuentasBancariasEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["id"]=pk
        return context

class CobranzasPorConfirmarView(LoginRequiredMixin, generic.ListView):
    model = Documentos_cabecera
    template_name = "cuentasconjuntas/listacobranzasporconfirmar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        return Documentos_cabecera.objects\
            .filter(leliminado = False, ldepositoencuentaconjunta = True
                , cxestado = 'A')
    # def get_queryset(self):
    #     cobranzas = Documentos_cabecera.objects.filter(cxestado='A'\
    #         , leliminado = False\
    #         , ldepositoencuentaconjunta = True\
    #         , cxtipofactoring__lanticipatotalnegociado = False )\
    #             .values('cxcliente__cxcliente__ctnombre','ddeposito'
    #             ,'cxtipofactoring__ctabreviacion'
    #             ,'cxcobranza','cxformapago','nvalor', 'cxcuentadeposito__cxcuenta'
    #             , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'C'",'')
    #             ,depositoencuentaconjunta=RawSQL("select ldepositoencuentaconjunta",'')
    #             )
                
    #     recuperaciones = Recuperaciones_cabecera.objects.filter(cxestado='A'\
    #         , leliminado = False\
    #         , ldepositoencuentaconjunta = True\
    #         , cxtipofactoring__lanticipatotalnegociado = False )\
    #             .values('cxcliente__cxcliente__ctnombre','ddeposito'
    #             ,'cxtipofactoring__ctabreviacion'
    #             ,'cxrecuperacion','cxformacobro','nvalor', 'cxcuentadeposito__cxcuenta'
    #             , 'id', 'cxcheque_id').annotate(tipo=RawSQL("select 'R'",'')
    #             ,depositoencuentaconjunta=RawSQL("select False",'')
    #             )

    #     return cobranzas.union(recuperaciones)

class ConfirmacionCobranzaEdit(LoginRequiredMixin, generic.UpdateView):
    model = Documentos_cabecera
    context_object_name='consulta'
    form_class = CuentasBancariasForm
    success_url= reverse_lazy("cuentasconjuntas:listadocuentas")
    login_url = 'bases:login'

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

def ConfirmarCobranza(request, cobranza_id, tipo_operacion):
    template_name = "cuentasconjuntas/datosconfirmacioncobranza_form.html"
    operacion = None
    
    if tipo_operacion=='C':
        cobr = Documentos_cabecera.objects.filter(pk=cobranza_id).first()
    else:
        cobr = Recuperaciones_cabecera.objects.filter(pk=cobranza_id).first()

    contexto={"operacion": operacion
        , "form_cargos" : DebitosForm
        , "form_transferencias" : TransferenciasForm
        , "tipo_operacion": tipo_operacion
        }
    
    return render(request, template_name, contexto)
