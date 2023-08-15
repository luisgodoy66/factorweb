from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic
from django.http import HttpResponse, JsonResponse
# from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.urls import reverse_lazy
# from django.db.models import Count, Sum, Q
from django.db.models.expressions import RawSQL 

from .models import Cuentas_bancarias, Movimientos, Transferencias
from cobranzas.models import Documentos_cabecera, Recuperaciones_cabecera\
    , DebitosCuentasConjuntas
from operaciones.models import Notas_debito_cabecera, Notas_debito_detalle\
    , Cargos_detalle
from bases.models import Usuario_empresa
from solicitudes.models import Asignacion
from empresa import models as Empresa_modelo

from .forms import CuentasBancariasForm, DebitosForm, TransferenciasForm\
    , DebitosNuevosForm

from bases.views import enviarPost, SinPrivilegios

import json

class CuentasView(SinPrivilegios, generic.ListView):
    model = Cuentas_bancarias
    template_name = "cuentasconjuntas/listacuentasbancarias.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="cuentasconjuntas.view_cuentas_bancarias"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Cuentas_bancarias.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(CuentasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class CuentasBancariasNew(SinPrivilegios, generic.CreateView):
    model = Cuentas_bancarias
    template_name = "cuentasconjuntas/datoscuentabancaria_modal.html"
    context_object_name='cuentas'
    form_class = CuentasBancariasForm
    success_url= reverse_lazy("cuentasconjuntas:listacuentasconjuntas")
    login_url = 'bases:login'
    permission_required="cuentasconjuntas.add_cuentas_bancarias"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CuentasBancariasNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasBancariasNew, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CuentasBancariasEdit(SinPrivilegios, generic.UpdateView):
    model = Cuentas_bancarias
    template_name = "cuentasconjuntas/datoscuentabancaria_modal.html"
    context_object_name='cuentas'
    form_class = CuentasBancariasForm
    success_url= reverse_lazy("cuentasconjuntas:listacuentasconjuntas")
    login_url = 'bases:login'
    permission_required="cuentasconjuntas.change_cuentas_bancarias"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')

        context = super(CuentasBancariasEdit, self).get_context_data(**kwargs)
        context["nueva"]=False
        context["id"]=pk
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(CuentasBancariasEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

class CobranzasPorConfirmarView(SinPrivilegios, generic.ListView):
    model = Documentos_cabecera
    template_name = "cuentasconjuntas/listacobranzasporconfirmar.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="cobranzas.change_documentos_cabecera"

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        
        cobranzas = Documentos_cabecera.objects.filter(cxestado='A'\
            , leliminado = False\
            , empresa = id_empresa.empresa
            , ldepositoencuentaconjunta = True\
            , cxtipofactoring__lanticipatotalnegociado = False )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito', 'cxcheque_id'
                ,'cxtipofactoring__ctabreviacion', 'cxcuentaconjunta__cxcuenta'
                ,'cxcobranza','cxformapago','nvalor', 'id', 'cxcuentaconjunta_id'
                , 'cxcuentaconjunta__cxbanco__ctbanco').annotate(tipo=RawSQL("select 'C'",'')
                )
                
        recuperaciones = Recuperaciones_cabecera.objects.filter(cxestado='A'\
            , leliminado = False\
            , empresa = id_empresa.empresa
            , ldepositoencuentaconjunta = True\
            , cxtipofactoring__lanticipatotalnegociado = False )\
                .values('cxcliente__cxcliente__ctnombre','ddeposito', 'cxcheque_id'
                ,'cxtipofactoring__ctabreviacion', 'cxcuentaconjunta__cxcuenta'
                ,'cxrecuperacion','cxformacobro','nvalor', 'id', 'cxcuentaconjunta_id'
                , 'cxcuentaconjunta__cxbanco__ctbanco').annotate(tipo=RawSQL("select 'R'",'')
                )
        return cobranzas.union(recuperaciones)

    def get_context_data(self, **kwargs):
        context = super(CobranzasPorConfirmarView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class CargosPendientesView(SinPrivilegios, generic.ListView):
    model = DebitosCuentasConjuntas
    template_name = "cuentasconjuntas/listacargospendientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="cobranzas.view_debitoscuentasconjuntas"

    def get_queryset(self):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        return DebitosCuentasConjuntas.objects\
            .filter(leliminado = False
                    , empresa = id_empresa.empresa
                    , notadedebito__nsaldo__gt = 0)

    def get_context_data(self, **kwargs):
        context = super(CargosPendientesView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

class DebitoBancarioEdit(SinPrivilegios, generic.UpdateView):
    model = DebitosCuentasConjuntas
    template_name = "cuentasconjuntas/datosdebitobancario_form.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    form_class = DebitosForm
    success_url= reverse_lazy("cuentasconjuntas:listacargospendientes")
    permission_required="cobranzas.change_debitoscuentasconjuntas"

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        # obtener el id de la nota de debito
        nd = DebitosCuentasConjuntas.objects.filter(pk=pk).first()

        context = super(DebitoBancarioEdit, self).get_context_data(**kwargs)
        context["id_notadedebito"]=nd.notadedebito.id
        context["notadedebito"]=nd.notadedebito
        context["cuentaconjunta"]=nd.cuentabancaria
        context["cliente"]=nd.notadedebito.cxcliente
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id

        # actualizar el resto de tablas involucradas en la grabacion del debito
        id_nd =self.request.POST["id_nd"]
        codigo_nd =self.request.POST["nd"]
        fecha = self.request.POST["dmovimiento"]
        valor = self.request.POST["nvalor"]

        # notas de debito
        nd = Notas_debito_cabecera.objects.filter(id=id_nd).first()
        nd.dnotadebito = fecha
        nd.nvalor = valor
        nd.nsaldo = valor
        nd.cxusuariomodifica = self.request.user.id
        nd.save()

        # movimiento
        mov = Movimientos.objects.filter(cxmovimiento=codigo_nd).first()
        mov.nvalor = valor
        mov.dmovimiento = fecha
        mov.cxusuariomodifica = self.request.user.id
        mov.save()

        # detalle de nd. Solo hay un registro de detalle cuando es cuenta conjunta
        nd_det = Notas_debito_detalle.objects\
                .filter(notadebito = id_nd).first()
        nd_det.nvalor = valor
        nd_det.save()
        
        # cargo
        cargo = Cargos_detalle.objects.filter(pk = nd_det.cargo.id).first()
        cargo.dultimageneracioncargos = fecha
        cargo.nvalor = valor
        cargo.nsaldo = valor
        cargo.ctvalorbase = valor
        cargo.cxusuariomodifica = self.request.user.id
        cargo.save()

        return super().form_valid(form)

class TransferenciasView(SinPrivilegios, generic.ListView):
    model = Transferencias
    template_name = "cuentasconjuntas/listatransferencias.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="cuentasconjuntas.view_transferencias"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Transferencias.objects.filter(leliminado = False, empresa = id_empresa.empresa)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(TransferenciasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

# class TansferenciaNew(SinPrivilegios, generic.CreateView):
#     model = Transferencias
#     template_name = "cuentasconjuntas/datostransferencia_form.html"
#     context_object_name='transferencias'
#     form_class = TransferenciasForm
#     success_url= reverse_lazy("cuentasconjuntas:listatransferencias")
#     login_url = 'bases:login'
#     permission_required="cuentasconjuntas.add_transferencias"

#     def form_valid(self, form):
#         id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
#         form.instance.empresa = id_empresa.empresa
#         form.instance.cxusuariocrea = self.request.user
#         # NOTA: obtener el id de la transaccion
#         print('form.intance',form.instance)
#         cb = self.request.POST.get("cuentaorigen")
#         cuenta = Cuentas_bancarias.objects.filter(pk = cb).first()
#         ft = self.request.POST.get("dmovimiento")
#         vt = self.request.POST.get("nvalor")
#         id = form.instance
#         mov = Movimientos(cuentabancaria=cuenta,
#                     dmovimiento=ft,
#                     nvalor=vt,
#                     cxtipo='T',
#                     cxmovimiento=id
#                     )
#         if mov:
#             mov.save()

#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super(TansferenciaNew, self).get_context_data(**kwargs)
#         sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
#         context['solicitudes_pendientes'] = sp
#         return context

#     def get_form_kwargs(self):
#         kwargs = super(TansferenciaNew, self).get_form_kwargs()
#         id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
#         kwargs['empresa'] = id_empresa.empresa
#         return kwargs

class TansferenciaEdit(SinPrivilegios, generic.UpdateView):
    model = Transferencias
    template_name = "cuentasconjuntas/datostransferencia_form.html"
    context_object_name='transferencias'
    form_class = TransferenciasForm
    success_url= reverse_lazy("cuentasconjuntas:listatransferencias")
    login_url = 'bases:login'
    permission_required="cuentasconjuntas.change_transferencias"

    def form_valid(self, form):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TansferenciaEdit, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
        context['solicitudes_pendientes'] = sp
        return context

    def get_form_kwargs(self):
        kwargs = super(TansferenciaEdit, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

def ConfirmarCobranza(request, cobranza_id, tipo_operacion, cuenta_conjunta):
    template_name = "cuentasconjuntas/datosconfirmacioncobranza_form.html"

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    cc = Cuentas_bancarias.objects.filter(pk = cuenta_conjunta).first()

    sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
    
    contexto={"id_operacion": cobranza_id
        , "form_cargos" : DebitosForm
        , "form_transferencias" : TransferenciasForm(empresa = id_empresa.empresa)
        , "tipo_operacion": tipo_operacion
        , 'cuenta_conjunta': cc
        , 'id_cuenta_conjunta': cuenta_conjunta
        , 'solicitudes_pendientes':sp
        }
    
    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('cobranzas.change_documentos_cabecera', login_url='bases:sin_permisos')
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

@login_required(login_url='/login/')
@permission_required('operaciones.add_notas_debito_cabecera', login_url='bases:sin_permisos')
def DebitoBancarioSinCobranza(request):
    template_name = "cuentasconjuntas/datosdebitobancario_form.html"
    sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()

    contexto={ "form" : DebitosNuevosForm
              , "solicitudes_pendientes" : sp    }

    if request.method =='POST':
        resultado = 'OK'

        id_cuentaorigen = request.POST.get("cuentabancaria")

        cuenta = Cuentas_bancarias.objects.filter(pk = id_cuentaorigen).first()

        cliente_id = cuenta.cxcliente.id
        valor_cargo = request.POST.get("nvalor")
        motivo_cargo = request.POST.get("ctmotivo")
        fecha_cargo = request.POST.get("dmovimiento")
        nusuario = request.user.id
        
        resultado=enviarPost("CALL uspAceptaCargoCuentaConjuntaSinCobranza( {0}\
            ,{1},{2},{3},'{4}','{5}','',0)"
            .format( nusuario
                , cliente_id, id_cuentaorigen, valor_cargo, motivo_cargo, fecha_cargo))


        if resultado=='OK':
            return redirect('cuentas_conjuntas:listacargospendientes')

        return HttpResponse(resultado)

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('cobranzas.change_debitoscuentasconjuntas', login_url='bases:sin_permisos')
def EliminarNotaDebito(request, pk):
    resultado = 'OK'

    ndcc = DebitosCuentasConjuntas.objects.filter(pk = pk).first()
    if ndcc:
        with transaction.atomic():
            ndcc.leliminado = True
            ndcc.cxusuarioelimina = request.user.id
            ndcc.save()

            # eliminar también la nota de débito
            nd = Notas_debito_cabecera.objects.filter(pk = ndcc.notadedebito.id).first()
            if nd:
                nd.leliminado = True
                nd.cxusuarioelimina = request.user.id
                nd.save()
            else:
                resultado='Nota de débito no encontrada.'
    else:
        resultado="No se ha podido obtener el registro de la nota de débito"

    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('cuentasconjuntas.change_transferencias', login_url='bases:sin_permisos')
def EliminarTransferencia(request, pk):
    # la eliminacion es lógica
    resultado = 'OK'
    transferencia = Transferencias.objects.filter(pk=pk).first()

    if not transferencia:
        return HttpResponse("Transferencia no encontrada")

    if request.method=="GET":

        with transaction.atomic():

            # marcar como eliminado
            transferencia.leliminado = True
            transferencia.cxusuarioelimina = request.user.id
            transferencia.save()

            # eliminar el movimiento de transferencias ...
            movimiento = Movimientos.objects.filter(cxmovimiento=pk
                                                    , cxtipo='T').first()

            # ... si es que existe una cuenta favorita
            if movimiento:
                movimiento.leliminado = True
                movimiento.cxusuarioelimina = request.user.id
                movimiento.save()
            else:
                resultado = "Movimiento no encontrado."
        
        if resultado!='OK':
            transaction.rollback()

    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('cuentasconjuntas.add_transferencias', login_url='bases:sin_permisos')
def DatosTransferencia(request, pk = None):
    template_name = "cuentasconjuntas/datostransferencia_form.html"
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    form = TransferenciasForm(empresa = id_empresa.empresa)
    
    sp = Asignacion.objects.filter(cxestado='P').filter(leliminado=False).count()
    
    contexto={'form':form
            , 'solicitudes_pendientes':sp
            }
    
    if request.method=='POST':
        co = request.POST.get("cuentaorigen")
        cd = request.POST.get("cuentadestino")
        cuentaorigen = Cuentas_bancarias.objects.filter(pk = co).first()
        cuentadestino = Empresa_modelo.Cuentas_bancarias.objects.filter(pk = cd).first()
        with transaction.atomic():
            # if not pk:
            trans = Transferencias(
                cuentaorigen = cuentaorigen,
                cuentadestino = cuentadestino,
                nvalor = request.POST.get("nvalor"),
                ndevolucion = request.POST.get("ndevolucion"),
                dmovimiento = request.POST.get("dmovimiento"),
                empresa = id_empresa.empresa,
                cxusuariocrea = request.user
            )
            if trans:
                trans.save()

#           movimiento
            mov = Movimientos(
                cuentabancaria = trans.cuentaorigen,
                dmovimiento = trans.dmodificacion,
                nvalor = trans.nvalor,
                cxtipo = 'T',
                cxmovimiento = trans.id,
                empresa = id_empresa.empresa,
                cxusuariocrea = request.user
            )
            if mov:
                mov.save()

        return redirect("cuentasconjuntas:listatransferencias")

    return render(request, template_name, contexto)
    