from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponse, JsonResponse
# from django.contrib.auth.decorators import login_required, permission_required
# from django.db import transaction
from django.urls import reverse_lazy
# from django.db.models import Count, Sum, Q
from django.db.models.expressions import RawSQL 

from .models import Cuentas_bancarias, Movimientos
from cobranzas.models import Documentos_cabecera, Recuperaciones_cabecera\
    , DebitosCuentasConjuntas

from .forms import CuentasBancariasForm, DebitosForm, TransferenciasForm
from bases.views import enviarPost, numero_a_letras

import json

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

# class ConfirmacionCobranzaEdit(LoginRequiredMixin, generic.UpdateView):
#     model = Documentos_cabecera
#     context_object_name='consulta'
#     form_class = CuentasBancariasForm
#     success_url= reverse_lazy("cuentasconjuntas:listadocuentas")
#     login_url = 'bases:login'

#     def form_valid(self, form):
#         form.instance.cxusuariocrea = self.request.user
#         return super().form_valid(form)

class CargosPendientesView(LoginRequiredMixin, generic.ListView):
    model = DebitosCuentasConjuntas
    template_name = "cuentasconjuntas/listacargospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        return DebitosCuentasConjuntas.objects\
            .filter(leliminado = False, notadedebito__nsaldo__gt = 0)

class DebitoBancarioEdit(LoginRequiredMixin, generic.UpdateView):
    model = DebitosCuentasConjuntas
    template_name = "cuentasconjuntas/datosdebitobancario_form.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    form_class = DebitosForm
    success_url= reverse_lazy("cuentasconjuntas:listadocargospendientes")

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        # actualizar el resto de tablas involucradas en la grabacion del debito
        # print(self.request)
        return super().form_valid(form)

def ConfirmarCobranza(request, cobranza_id, tipo_operacion, cuenta_conjunta):
    template_name = "cuentasconjuntas/datosconfirmacioncobranza_form.html"

    cc = Cuentas_bancarias.objects.filter(pk = cuenta_conjunta).first()

    contexto={"id_operacion": cobranza_id
        , "form_cargos" : DebitosForm
        , "form_transferencias" : TransferenciasForm
        , "tipo_operacion": tipo_operacion
        , 'cuenta_conjunta': cc
        , 'id_cuenta_conjunta': cuenta_conjunta
        }
    
    return render(request, template_name, contexto)


def AceptarConfirmacion(request):
    # ejecuta un store procedure 
    # Devuelve el control a un proceso js
    resultado = 'OK'

    objeto=json.loads(request.body.decode("utf-8"))

    tipo_operacion=objeto["pstipooperacion"]
    id_cobranza=objeto["pncobranza"]
    hay_transferencia = objeto ["pltransferencia"] 
    valor_transferencia = objeto ["pntransferencia"] 
    valor_devolucion = objeto ["pndevolucion"] 
    id_cuentadestino = objeto ["pncuentadestino"] 
    id_cuentaorigen = objeto ["pncuentaorigen"] 
    fecha_transferencia = objeto ["pdtransferencia"] 
    hay_cargo = objeto ["plcargo"] 
    valor_cargo = objeto ["pncargo"] 
    motivo_cargo = objeto ["psmotivo"] 
    fecha_cargo = objeto ["pdcargo"]

    nusuario = request.user.id
    
    if hay_transferencia :
        if not id_cuentadestino :
            return HttpResponse("Debe especificar la cuenta destino de transferencia")
    else:
        id_cuentadestino = 'Null'

    resultado=enviarPost("CALL uspConfirmarCobranzaCuentaConjunta( '{0}',{1},{2},{3}\
        ,{4},{5},{6},{7}\
        ,'{8}',{9},{10},'{11}','{12}','',0)"
        .format(tipo_operacion, id_cobranza, nusuario, hay_transferencia
        , valor_transferencia, valor_devolucion, id_cuentadestino, id_cuentaorigen
        ,fecha_transferencia,hay_cargo,valor_cargo, motivo_cargo, fecha_cargo))

    return HttpResponse(resultado)