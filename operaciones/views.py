import json
# from unicodedata import decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date

from .forms import DatosOperativosForm, AsignacionesForm, \
    MaestroMovimientosForm, CondicionesOperativasForm, \
    DetalleCondicionesOperativasForm, TasasDocumentosForm, \
    TasasAccesoriosForm, DesembolsarForm, AnexosForm

from .models import Cargos_detalle, Condiciones_operativas_detalle, Datos_operativos \
    , Asignacion,  Movimientos_maestro, Condiciones_operativas_cabecera, Anexos\
    , Desembolsos, Documentos
from empresa.models import  Clases_cliente, Datos_participantes, \
    Tasas_factoring, Tipos_factoring, Cuentas_bancarias

from solicitudes import models as ModelosSolicitud
from clientes import models as ModeloCliente

from datetime import date, timedelta
from decimal import Decimal
from docxtpl import DocxTemplate, InlineImage

FACTURAS_PURAS = 'F'
FACTURAS_CON_ACCESORIOS = 'A'

class DatosOperativosView(LoginRequiredMixin, generic.ListView):
    model = ModeloCliente.Datos_generales
    template_name = "operaciones/listadatosoperativos.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class AsignacionesView(LoginRequiredMixin, generic.ListView):
    model = Asignacion
    template_name = "operaciones/listaasignaciones.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class AsignacionesConsulta(LoginRequiredMixin, generic.ListView):
    model = Asignacion
    template_name = "operaciones/consultageneralasignaciones.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        desde = date.today() + timedelta(days=-date.today().day +1)
        hasta = date.today()

        context = super(AsignacionesConsulta, self).get_context_data(**kwargs)
        context["desde"] = desde
        context["hasta"] =hasta
        return context

class AsignacionesPendientesDesembolsarView(LoginRequiredMixin, generic.ListView):
    model = Asignacion
    template_name = "operaciones/listaasignacionespendientesdesembolsar.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    def get_queryset(self):
        # 22-ene-23 l.g.    cambiar A por L(iquidada)
        # return Asignacion.objects.filter(cxestado='A',\
        return Asignacion.objects.filter(cxestado='L',\
            leliminado = False, ddesembolso__lte = date.today())

class MaestroMovimientosView(LoginRequiredMixin, generic.ListView):
    model = Movimientos_maestro
    template_name = "operaciones/listamaestromovimientos.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    
class MaestroMovimientoNew(LoginRequiredMixin, generic.CreateView):
    # permission_required="clientes.add_Linea_factoring"
    model = Movimientos_maestro
    template_name="operaciones/datosmovimiento_form.html"
    context_object_name = "consulta"
    form_class=MaestroMovimientosForm
    success_url=reverse_lazy("operaciones:listamaestromovimientos")
    success_message="Movimiento creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class MaestroMovimientoEdit(LoginRequiredMixin, generic.UpdateView):
    model = Movimientos_maestro
    template_name="operaciones/datosmovimiento_form.html"
    context_object_name = "consulta"
    form_class=MaestroMovimientosForm
    success_url=reverse_lazy("operaciones:listamaestromovimientos")
    success_message="Movimiento actualizada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

class CondicionesOperativasView(LoginRequiredMixin, generic.ListView):
    model = Condiciones_operativas_cabecera
    template_name= "operaciones/listacondicionesoperativas.html"
    context_object_name= 'consulta'
    login_url = 'bases:login'

class AnexosView(LoginRequiredMixin, generic.ListView):
    model = Anexos
    template_name = "operaciones/listaanexos.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class AnexosNew(LoginRequiredMixin, generic.CreateView):
    model = Anexos
    template_name="operaciones/datosanexo_form.html"
    context_object_name = "anexo"
    form_class=AnexosForm
    success_url=reverse_lazy("operaciones:listaanexos")
    success_message="Anexo creado satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class AnexosEdit(LoginRequiredMixin, generic.UpdateView):
    # permission_required="clientes.add_Linea_factoring"
    model = Anexos
    template_name="operaciones/datosanexo_form.html"
    context_object_name = "anexo"
    form_class=AnexosForm
    success_url=reverse_lazy("operaciones:listaanexos")
    success_message="Anexo creado satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

@login_required(login_url='/login/')
@permission_required('operativos.update_asignacion', login_url='bases:sin_permisos')
def DesembolsarAsignacion(request, pk, cliente_ruc):
    template_name = "operaciones/datosdesembolsoaclientes_form.html"
    contexto = {}
    formulario={}

    cliente = ModeloCliente.Datos_generales.objects\
        .filter(cxcliente=cliente_ruc).first()

    datosoperativos = Datos_operativos.objects.filter(cxcliente = cliente_ruc).first()
    
    cuenta_transferencia = ModeloCliente.Cuenta_transferencia\
            .objects.cuenta_default(cliente_ruc).first()
    
    asignacion = Asignacion.objects.filter(pk=pk).first()

    if request.method=="GET":

        e={'cxtipooperacion':'A'
            , 'cxoperacion':asignacion.id
            , 'nvalor': asignacion.neto()
            }
        formulario = DesembolsarForm(e)

        contexto={'liquidacion':asignacion.dnegociacion
            , 'instruccion_de_pago':asignacion.ctinstrucciondepago
            , "cuenta_transferencia":cuenta_transferencia
            , 'id_beneficiario': datosoperativos.cxbeneficiarioasignacion
            , 'beneficiario': datosoperativos.ctbeneficiarioasignacion
            , "form":formulario
            , 'cliente':cliente
            , 'tipo_operacion':'A'
            , 'operacion':asignacion.cxasignacion
        }

    if request.method=="POST":

        with transaction.atomic():
            # 1. Actualizar el estado de la ASIGNACION
            # Cambiar L por P(agada)
            # asignacion.cxestado = 'L'
            asignacion.cxestado = 'P'
            asignacion.save()

            # 2. Cobrar los cargos generados por la negociación
            # (Se generaron en la aceptacion)

            valor = asignacion.nanticipo

            cargos = Cargos_detalle.objects\
                .filter(cxasignacion=asignacion\
                    , cxcliente_id=cliente_ruc).all()

            for cargo in cargos:
                if valor >= cargo.nsaldo:
                    cargo.nsaldo = 0
                    cargo.save()
                    valor = valor - cargo.nsaldo
                else:
                    cargo.nsaldo = cargo.nsaldo - valor
                    cargo.save()
                    valor = 0

            # 3. grabar el desembolso
            operacion = request.POST.get("cxoperacion")
            forma_pago = request.POST.get("cxformapago")

            if forma_pago =="MOV":
                cuenta_pago = None
            else:
                x = request.POST.get("cxcuentapago")
                cuenta_pago = Cuentas_bancarias.objects.filter(pk = x).first()

            if forma_pago=="CHE":
                id_beneficiario = datosoperativos.cxbeneficiarioasignacion
                beneficiario = datosoperativos.ctbeneficiarioasignacion
            else:
                id_beneficiario=None
                beneficiario=None

            if forma_pago =="TRA":
                cuenta_destino = cuenta_transferencia
            else:
                cuenta_destino = None

            liquidacion = Desembolsos(cxtipooperacion='A'
                , cxoperacion = operacion
                , cxcliente = cliente
                , nvalor = asignacion.neto()
                , cxformapago = forma_pago
                , cxcuentapago = cuenta_pago
                , cxbeneficiario =id_beneficiario
                , ctbeneficiario = beneficiario
                , cxcuentadestino = cuenta_destino
                , cxusuariocrea = request.user
                )
            
            liquidacion.save()

        return redirect("operaciones:listaasignacionespendientesdesembolsar")

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('operativos.view_datos_operativos', login_url='bases:sin_permisos')
def DatosOperativos(request, cliente_ruc=None):
    template_name="operaciones/datosoperativos_form.html"
    contexto={}
    formulario={}
    datoscliente={}
    
    cliente = ModeloCliente.Datos_generales.objects\
        .filter(cxcliente=cliente_ruc).first()

    if request.method=='GET':
        datoscliente = Datos_operativos.objects\
            .filter(cxcliente=cliente_ruc).first()
        if datoscliente:
            dalta= date.isoformat(datoscliente.dalta)
            e={ 
                'cxcliente':datoscliente.cxcliente,
                'dalta':dalta,
                'cxclase':datoscliente.cxclase,
                'nporcentajeanticipo':datoscliente.nporcentajeanticipo,
                'ntasacomision':datoscliente.ntasacomision,
                'ntasadescuentocartera':datoscliente.ntasadescuentocartera,
                'ntasagaoa':datoscliente.ntasagaoa,
                'cxbeneficiarioasignacion':datoscliente.cxbeneficiarioasignacion,
                'ctbeneficiarioasignacion':datoscliente.ctbeneficiarioasignacion,
                'cxbeneficiariocobranzas':datoscliente.cxbeneficiariocobranzas,
                'ctbeneficiariocobranzas':datoscliente.ctbeneficiariocobranzas,
                'cxestado':datoscliente.cxestado
            }
            formulario=DatosOperativosForm(e)
        else:
            formulario=DatosOperativosForm()

    contexto={'nombrecliente':cliente
            , 'form_cliente':formulario
            }

    if request.method=='POST':

        dalta = request.POST.get("dalta")
        cxclase = request.POST.get("cxclase")
        nporcentajeanticipo = request.POST.get("nporcentajeanticipo")
        ntasacomision = request.POST.get("ntasacomision")
        ntasadescuentocartera = request.POST.get("ntasadescuentocartera")
        ntasagaoa = request.POST.get("ntasagaoa")
        id_beneficiario_asgn = request.POST.get("cxbeneficiarioasignacion")
        beneficiario_asgn = request.POST.get("ctbeneficiarioasignacion")
        id_beneficiario_cobr = request.POST.get("cxbeneficiariocobranzas")
        beneficiario_cobr = request.POST.get("ctbeneficiariocobranzas")
        estado = request.POST.get('cxestado')

        idclase = Clases_cliente.objects\
            .filter(cxclase = cxclase).first()

        datoscliente = Datos_operativos.objects\
            .filter(cxcliente=cliente).first()

        if not datoscliente:
            datoscliente= Datos_operativos(
                dalta = dalta,
                cxclase=idclase,
                nporcentajeanticipo=nporcentajeanticipo,
                cxcliente = cliente,
                ntasacomision = ntasacomision,
                ntasadescuentocartera = ntasadescuentocartera,
                ntasagaoa = ntasagaoa,
                cxbeneficiarioasignacion = id_beneficiario_asgn,
                ctbeneficiarioasignacion = beneficiario_asgn,
                cxbeneficiariocobranzas = id_beneficiario_cobr,
                ctbeneficiariocobranzas = beneficiario_cobr,
                cxusuariocrea = request.user,
                cxestado = estado
            )
            if datoscliente:
                datoscliente.save()
        else:
            datoscliente.dalta=dalta
            datoscliente.cxclase = idclase
            datoscliente.nporcentajeanticipo=nporcentajeanticipo
            datoscliente.ntasacomision=ntasacomision
            datoscliente.ntasadescuentocartera=ntasadescuentocartera
            datoscliente.ntasagaoa=ntasagaoa
            datoscliente.cxbeneficiarioasignacion = id_beneficiario_asgn
            datoscliente.ctbeneficiarioasignacion = beneficiario_asgn
            datoscliente.cxbeneficiariocobranzas = id_beneficiario_cobr
            datoscliente.ctbeneficiariocobranzas = beneficiario_cobr
            datoscliente.cxusuariomodifica = request.user.id
            datoscliente.cxestado= estado

            datoscliente.save()

        # nota: crear un registro historico del cambio realizado

        return redirect("operaciones:listadatosoperativos")

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('operativos.create_asignacion', login_url='bases:sin_permisos')
def AceptarAsignacion(request, asignacion_id=None):
    template_name="operaciones/aceptarasignacion_form.html"
    asignacion = {}
    formulario = {}
    contexto={}
    iva_gao = 'No'
    iva_dc = 'No'
    formulario=AsignacionesForm()
    carga_gao= "No"
    carga_dc = "No"
    condicion_operativa={}
    beneficiario = ''

    asignacion = ModelosSolicitud.Asignacion.objects\
        .filter(pk=asignacion_id).first()

    cuenta_transferencia = ModeloCliente.Cuenta_transferencia\
            .objects.cuenta_default(asignacion.cxcliente.cxcliente).first()
            
    # buscar el tipo de factoring 
    tipo_factoring = Tipos_factoring.objects.get(cxtipofactoring=asignacion.cxtipofactoring_id)
    if not tipo_factoring:
        return HttpResponse("Tipo de factoring no existe:" + asignacion.cxtipofactoring_id)
    if tipo_factoring.lgeneradcenaceptacion:
        carga_dc="Si"
    if tipo_factoring.lgeneragaoenaceptacion:
        carga_gao="Si"

    # si tipo de factoring usa condición operativa cargarla
    if tipo_factoring.lmanejacondicionesoperativas:
        if asignacion.cxtipo ==FACTURAS_PURAS:
            condicion_operativa = Condiciones_operativas_cabecera.objects \
                .filter(cxtipofactoring= tipo_factoring\
                    ,leliminado = False\
                    ,laplicaafacturaspuras=True)
        else:
            if asignacion.cxtipo==FACTURAS_CON_ACCESORIOS:
                condicion_operativa = Condiciones_operativas_cabecera.objects \
                    .filter(cxtipofactoring= tipo_factoring\
                        ,leliminado = False\
                        ,laplicaaaccesorios=True)
            else:
                return ("Tipo de asignación no aceptado")

        if not condicion_operativa:
            return HttpResponse("No hay condiciones operativas activas para este tipo de factoring")
            
    # datos de tasa gao/dc
    gao = Tasas_factoring.objects.filter(cxtasa="GAO").first()
    if not gao:
        return HttpResponse("no encontró tasa de gao")
    if gao.lcargaiva: iva_gao = 'Si'

    dc = Tasas_factoring.objects.filter(cxtasa="DCAR").first()
    if not dc:
        return HttpResponse("no encontró tasa de descuento de catera")
    if dc.lcargaiva: iva_dc='Si'

    dic_gao  = {'carga_iva': iva_gao
        , 'descripcion': gao.ctdescripcionenreporte
        , 'generar': carga_gao
        , 'iniciales': gao.ctinicialesentablas}

    dic_dc = {'carga_iva': iva_dc
        , 'descripcion': dc.ctdescripcionenreporte
        , 'generar':carga_dc
        , 'iniciales': dc.ctinicialesentablas}

    # buscar en datos operativos el beneficiario del cheque
    datos_operativos = Datos_operativos.objects\
                .filter(cxcliente = asignacion.cxcliente.cxcliente).first()
    if datos_operativos:
        beneficiario=datos_operativos.ctbeneficiarioasignacion

    contexto={'form_asignacion':formulario,
        'asignacion': asignacion,
        'gao': dic_gao,
        'dc' : dic_dc,
        'usa_linea_factoring':tipo_factoring.lmanejalineafactoring,
        'condicion_operativa': condicion_operativa,
        'porcentaje_iva':12,
        'tipo_asignacion':asignacion.cxtipo,
        "cuenta_transferencia":cuenta_transferencia,
        "beneficiario": beneficiario,
    }

    return render(request, template_name, contexto)

from django.http import HttpResponse, JsonResponse

def DetalleCargosAsignacion(request, asignacion_id = None
                        , fecha_desembolso = None, condicion_id=None):
    asignacion = ModelosSolicitud.Asignacion.objects.get(pk=asignacion_id) 

    if not asignacion:
        return HttpResponse("Asignación "+ str(asignacion_id) + " no encontrada")

    # buscar el tipo de factoring 
    tipo_factoring = Tipos_factoring.objects.filter(cxtipofactoring=asignacion.cxtipofactoring_id).first()
    if not tipo_factoring:
        return HttpResponse("Tipo de factoring "+ asignacion.cxtipofactoring + " no existe")

    # buscar el cliente 
    cliente = ModelosSolicitud.Clientes.objects.filter(pk=asignacion.cxcliente_id).first()
    if not cliente:
        return HttpResponse("cliente "+asignacion.cxcliente_id + " no encontrado")
    
    # buscar los datos operativos 
    datos_operativos = Datos_operativos.objects.filter(cxcliente=cliente.cxcliente).first()
    if not datos_operativos:
        return HttpResponse("No se ha encontrado datos operativos del cliente.")

    # datos de tasa gao/dc
    gao = Tasas_factoring.objects.filter(cxtasa="GAO").first()
    if not gao:
        return HttpResponse("no encontró registro de tasa de gao en tabla de tasas de factoring")

    dc = Tasas_factoring.objects.filter(cxtasa="DCAR").first()
    if not dc:
        return HttpResponse("no encontró registro de tasa de descuento de catera en tabla de tasas de factoring")

    if not fecha_desembolso:
        return HttpResponse("No hay fecha de desembolso")

    # inicializar variables
    porcentaje_anticipo = 0
    tasa_gao = 0
    tasa_dc = 0
    clase_cliente=''
    buscar_anticipo_en_condicion_operativa = False
    buscar_gao_en_condicion_operativa = False
    buscar_descuento_en_condicion_operativa = False

    # determinar el porcentaje de anticipo
    if tipo_factoring.lanticipatotalnegociado:
        porcentaje_anticipo=100
    else:
        porcentaje_anticipo = datos_operativos.nporcentajeanticipo

    # obtener las tasas de los datos operativos del ciente
    tasa_gao = datos_operativos.ntasacomision
    tasa_dc = datos_operativos.ntasadescuentocartera
    clase_cliente = datos_operativos.cxclase

    # Si no hay tasas en los datos del cliente, preparar la lógica para usar las tasas de la condición operativa
    if tipo_factoring.lmanejacondicionesoperativas:
        if condicion_id == 0:
            return HttpResponse("No hay condicion operativa")
        if tasa_gao == 0 :
            buscar_gao_en_condicion_operativa=True

        if tasa_dc==0 :
            buscar_descuento_en_condicion_operativa=True

        if porcentaje_anticipo==0:
            buscar_anticipo_en_condicion_operativa=True

    fecha_desembolso = parse_date(fecha_desembolso)

    # recuperar los documentos
    # en caso que se trate de una asignacion con accesorios
    # , debe tomar los cheques

    if asignacion.cxtipo == FACTURAS_PURAS:
        documentos = ModelosSolicitud.Documentos.objects\
            .filter(cxasignacion=asignacion_id\
                ,leliminado = False)
    else:
       documentos = ModelosSolicitud.ChequesAccesorios.objects\
            .filter(documento__in=ModelosSolicitud.Documentos.objects
                .filter(cxasignacion=asignacion_id, leliminado = False)\
                    , leliminado = False)
            
    # calcular cargos
    for i in range(len(documentos)):
        CalcularCargosPorDocumento(documentos[i], gao ,dc, fecha_desembolso
                                    ,buscar_anticipo_en_condicion_operativa
                                    , buscar_gao_en_condicion_operativa
                                    , buscar_descuento_en_condicion_operativa 
                                    , porcentaje_anticipo, tasa_gao, tasa_dc
                                    , asignacion.cxtipo
                                    , clase_cliente, condicion_id)
    # crea página con datos json de cargos de documentos
    # return HttpResponse(GeneraDetalleParaTabla(asignacion_id, asignacion.cxtipo ))
    # 09-SEP-22 L.G.    no crea datos json, solo grabó datos. otro proceso crea los 
    #                   datos json
    return HttpResponse("OK")

def GeneraDetalleParaTabla(asignacion_id, tipo_asignacion):
    # es llamado en el proceso DetalleCargosAsignacion
    # crear detalle de salida para el contexto
    # recuperar los documentos

    if tipo_asignacion==FACTURAS_PURAS:
        documentos = ModelosSolicitud.Documentos.objects\
            .filter(cxasignacion=asignacion_id\
                ,leliminado = False)
    else:
        documentos = ModelosSolicitud.ChequesAccesorios.objects\
            .filter(documento__in=ModelosSolicitud.Documentos.objects
                .filter(cxasignacion=asignacion_id, leliminado = False)\
                    , leliminado = False)

    tempBlogs = []
    for i in range(len(documentos)):
        tempBlogs.append(DetalleDocumentoADiccionario(documentos[i], tipo_asignacion)) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraDetalleParaTabla1(request,asignacion_id):
    # Es invocado desde la url
    # crear detalle de salida para el contexto
    # no calcula, ni graba cargos, recupera los documentos
    asignacion = ModelosSolicitud.Asignacion.objects.get(pk=asignacion_id) 

    if asignacion.cxtipo==FACTURAS_PURAS:
        documentos = ModelosSolicitud.Documentos.objects\
            .filter(cxasignacion=asignacion_id\
                ,leliminado = False)
    else:
        documentos = ModelosSolicitud.ChequesAccesorios.objects\
            .filter(documento__in=ModelosSolicitud.Documentos.objects
                .filter(cxasignacion=asignacion_id, leliminado = False)\
                    , leliminado = False)

    tempBlogs = []
    for i in range(len(documentos)):
        tempBlogs.append(DetalleDocumentoADiccionario(documentos[i], asignacion.cxtipo)) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def CalcularCargosPorDocumento(doc, gao, dc, fecha_desembolso
                            , buscar_anticipo_en_condicion_operativa
                            , buscar_gao_en_condicion_operativa
                            , buscar_descuento_en_condicion_operativa
                            , porcentaje_anticipo, tasa_gao, tasa_dc
                            , tipo_asignacion
                            , clase_cliente = "A"
                            , condicion_id = None):
    # los dos ultimos parametros se omiten cuando se trata de edicion de tasas

    plazo = doc.dvencimiento - fecha_desembolso
    plazo = plazo.days
    clase_comprador = ''
    doc.nplazo = plazo

    # si usa condicion operativa buscar classe de comprador
    if buscar_anticipo_en_condicion_operativa \
        or buscar_gao_en_condicion_operativa \
        or buscar_descuento_en_condicion_operativa:

        # el comprador esta en el documento no en el cheque
        if tipo_asignacion==FACTURAS_PURAS:
            comprador = ModeloCliente.Datos_compradores.objects\
                .filter(cxcomprador = doc.cxcomprador).first()
        else:
            fac = ModelosSolicitud.Documentos.objects.filter(id = doc.documento_id).first()
            comprador = ModeloCliente.Datos_compradores.objects\
                .filter(cxcomprador_id = fac.cxcomprador).first()

        if comprador:
            clase_comprador = comprador.cxclase
        
        # ubicar el plazo en las condiciones operativas    
        condicion_plazo = Condiciones_operativas_detalle.objects\
            .ubicar_plazo(condicion_id, clase_cliente, clase_comprador, plazo).first()

        if condicion_plazo:
            if buscar_anticipo_en_condicion_operativa:
                porcentaje_anticipo= condicion_plazo.nporcentajeanticipo
            
            if buscar_gao_en_condicion_operativa :
                tasa_gao = condicion_plazo.ntasagao

            if buscar_descuento_en_condicion_operativa :
                tasa_dc = condicion_plazo.ntasadescuento
    
    doc.nporcentajeanticipo = porcentaje_anticipo
    doc.ntasacomision = tasa_gao
    doc.ntasadescuento = tasa_dc

    # anticipo
    doc.nanticipo = doc.ntotal * doc.nporcentajeanticipo / 100
    
    # gao
    if gao.lsobreanticipo:
        doc.ngao = (doc.ntotal * doc.nporcentajeanticipo * doc.ntasacomision / 10000)
    else:
        doc.ngao = (doc.ntotal * doc.ntasacomision / 100)

    if not gao.lflat:
        doc.ngao = (doc.ngao * plazo / gao.ndiasperiocidad)

    # dc
    if dc.lsobreanticipo:
        doc.ndescuentocartera = (doc.ntotal * doc.nporcentajeanticipo * doc.ntasadescuento / 10000)
    else:
        doc.ndescuentocartera = (doc.ntotal * doc.ntasadescuento / 100)

    if not dc.lflat:
        doc.ndescuentocartera = (doc.ndescuentocartera * plazo / dc.ndiasperiocidad)

    doc.save()

def DetalleDocumentoADiccionario(doc, tipo_asignacion):
    output = {}

    # el id debe ser del documento o el accesorio, para poder editar las tasas
    output['id'] = doc.id
    
    # los siguientes 3 campos pertenecen al documento y no se encuentran en los cheques
    if tipo_asignacion==FACTURAS_PURAS:
        output["Comprador"] = doc.ctcomprador
        output["Documento"] = doc.ctdocumento
        output["Emision"] = doc.demision.strftime("%Y-%m-%d")
    else:
        # output['id'] = doc.documento.id
        output["Comprador"] = doc.documento.ctcomprador
        output["Documento"] = doc.documento.ctdocumento
        output["Emision"] = doc.documento.demision.strftime("%Y-%m-%d")

    output["Vencimiento"] = doc.dvencimiento.strftime("%Y-%m-%d")
    output["Total"] = doc.ntotal
    output["Plazo"] = doc.nplazo
    output["Porc_anticipo"] = str(doc.nporcentajeanticipo)
    output["Valor_anticipo"] = doc.nanticipo
    output["Porc_GAO"] = round( doc.ntasacomision,2)
    output["Valor_GAO"] = doc.ngao
    output["Porc_DC"] = round(doc.ntasadescuento,2)
    output["Valor_DC"] = doc.ndescuentocartera

    return output

def SumaCargos(request,asignacion_id, gao_carga_iva, dc_carga_iva, carga_gao, carga_dc, porcentaje_iva=12):
    # lee los datos de la tabla solicutid documentos

    g=Decimal(0); d=Decimal(0); 
    a=0.0; iva=0.0; neto=0.0

    asignacion = ModelosSolicitud.Asignacion.objects.get(pk=asignacion_id) 

    if asignacion.cxtipo==FACTURAS_PURAS:
        documentos = ModelosSolicitud.Documentos.objects\
            .filter(cxasignacion=asignacion_id\
                ,leliminado = False)
    else:
        documentos = ModelosSolicitud.ChequesAccesorios.objects\
            .filter(documento__in=ModelosSolicitud.Documentos.objects
            .filter(cxasignacion=asignacion_id))\
            .filter(documento__in=ModelosSolicitud.Documentos.objects
            .filter(leliminado = False))\
                .filter( leliminado = False)

    # total negociado
    negociado = documentos.aggregate(Sum('ntotal'))
    n = negociado["ntotal__sum"]
    
    # anticipo
    total_anticipo = documentos.aggregate(Sum('nanticipo'))
    a = total_anticipo["nanticipo__sum"]

    # gao
    if carga_gao=="Si":
        total_gao = documentos.aggregate(Sum('ngao'))
        g = total_gao["ngao__sum"]

    # dc
    if carga_dc=="Si":
        total_dc = documentos.aggregate(Sum('ndescuentocartera'))
        d = total_dc["ndescuentocartera__sum"]

    # iva
    base = 0
    if gao_carga_iva=="Si":
        base += g
    if dc_carga_iva=="Si":
        base += d
    iva = round( base * porcentaje_iva / 100,2)
    # redondear a 2 decimales?
    # neto
    neto =   a -g - d - iva

    data={'negociado': str(n)
        ,'gao':str(g)
        , 'dc':str(d)
        , 'anticipo': str(a)
        , 'iva': str(iva)
        , 'neto':str(neto)}

    return HttpResponse(json.dumps(data), content_type = "application/json")

def EditarTasasDocumentoSolicitud(request, documento_id, fecha_desembolso, asignacion_id):
    template_name = "operaciones/cambiotasa_modal.html"
    contexto={}
    formulario={}
    numero_documento=""
    # si son facturas puras los documentos son las facturas
    # si son accesorios los documentos son los cheques
    asignacion = ModelosSolicitud.Asignacion.objects.get(pk=asignacion_id) 
    if asignacion.cxtipo ==FACTURAS_PURAS:
        documento = ModelosSolicitud.Documentos.objects.filter(pk=documento_id).first()
        es_facturas_puras = True
    else:
        documento = ModelosSolicitud.ChequesAccesorios.objects.filter(pk=documento_id).first()
        es_facturas_puras = False


    if request.method=='GET':
        if documento:
            e={ 
                'nporcentajeanticipo':documento.nporcentajeanticipo,
                'ntasacomision':documento.ntasacomision,
                'ntasadescuento':documento.ntasadescuento,
            }
            if es_facturas_puras:
                formulario=TasasDocumentosForm(e)
                numero_documento=documento.ctdocumento
            else:
                formulario= TasasAccesoriosForm(e)
                numero_documento=documento.documento.ctdocumento
        else:
            if es_facturas_puras:
                formulario=TasasDocumentosForm()
            else:
                formulario= TasasAccesoriosForm()

    contexto={'form_documento':formulario
        , 'documento_id':documento_id
        , 'documento':numero_documento
        , 'fecha_desembolso': fecha_desembolso
        , 'asignacion':asignacion_id }

    if request.method=='POST':

        nporcentajeanticipo = request.POST.get("nporcentajeanticipo")
        ntasacomision = request.POST.get("ntasacomision")
        ntasadescuentocartera = request.POST.get("ntasadescuento")

        nporcentajeanticipo = Decimal(nporcentajeanticipo)
        ntasacomision = Decimal(ntasacomision)
        ntasadescuentocartera = Decimal(ntasadescuentocartera)
        
        # calcular y grabar los valores para cada tasa y grabarlos en el registro del documento
        # datos de tasa gao/dc
        gao = Tasas_factoring.objects.filter(cxtasa="GAO").first()
        dc = Tasas_factoring.objects.filter(cxtasa="DCAR").first()
        fecha_desembolso = parse_date(fecha_desembolso)
            
        # cuando edita no necesita enviar clase de cliente ni codigo de condicion operativa
        # si necesita el tipo de asignacion para saber donde grbar las tasas

        CalcularCargosPorDocumento(documento, gao ,dc, fecha_desembolso
                                    , False, False, False , nporcentajeanticipo
                                    , ntasacomision, ntasadescuentocartera
                                    , asignacion.cxtipo)
        return HttpResponse(1)

    return render(request, template_name, contexto)

from bases.views import enviarPost, numero_a_letras

def AceptarDocumentos(request):
    # ejecuta un store procedure 
    pslocalidad = ''

    objeto=json.loads(request.body.decode("utf-8"))

    pid_asignacion=objeto["id_asignacion"]
    pdnegociacion=objeto["dnegociacion"]
    pddesembolso=objeto["ddesembolso"]
    pnanticipo=objeto["nanticipo"]
    pngao=objeto["ngao"]
    pndescuentocartera=objeto["ndescuentocartera"]
    pniva=objeto["niva"]
    psinstruccionpago=objeto["sinstruccionpago"]
    nusuario = request.user.id

    resultado=enviarPost("CALL uspAceptarAsignacion( {0},'{1}', '{2}',{3},{4}\
        ,{5},{6},'{7}',{8},'{9}','')"
        .format(pid_asignacion,pdnegociacion,pddesembolso,pnanticipo,pngao\
            ,pndescuentocartera,pniva,psinstruccionpago,nusuario, pslocalidad))

    return HttpResponse(resultado)

@login_required(login_url='/login/')
@permission_required('operaciones.view_asignaciones', login_url='bases:sin_permisos')
def CondicionesOperativas(request,condicion_id=None):
    template_name='operaciones/datoscondicionesoperativas_form.html'
    formulario={}
    condicion={}

    if request.method=='GET':
        condicion = Condiciones_operativas_cabecera.objects.filter(pk=condicion_id).first()

        if condicion:
            e ={
                'ctcondicion': condicion.ctcondicion ,
                'cxtipofactoring': condicion.cxtipofactoring ,
                'lactiva': condicion.lactiva,
                'laplicaafacturaspuras': condicion.laplicaafacturaspuras ,
                'laplicaaaccesorios': condicion.laplicaaaccesorios ,
            }
            formulario = CondicionesOperativasForm(e)
        else:
            formulario = CondicionesOperativasForm()
            condicion=None
            
    contexto={'form_cabecera':formulario,
    'form_detalle': DetalleCondicionesOperativasForm,
    'condicion':condicion
    }
    
    if request.method=='POST':
        ctcondicion = request.POST.get("ctcondicion")
        cxtipofactoring = request.POST.get("cxtipofactoring")
        laplicaafacturaspuras = request.POST.get("laplicaafacturaspuras")
        laplicaaaccesorios = request.POST.get("laplicaaaccesorios")
        
        aplica_facturaspuras_on=False;aplica_accesorios_on=False
      
        if laplicaafacturaspuras: aplica_facturaspuras_on = True
        if laplicaaaccesorios: aplica_accesorios_on = True

        tipo_factoring = Tipos_factoring.objects.filter(cxtipofactoring=cxtipofactoring).first()

        if not condicion_id:
            condicion = Condiciones_operativas_cabecera(
                ctcondicion =ctcondicion,
                cxtipofactoring=tipo_factoring,
                laplicaafacturaspuras=aplica_facturaspuras_on,
                laplicaaaccesorios=aplica_accesorios_on,
                cxusuariocrea = request.user
            )
            if condicion:
                condicion.save()
                condicion_id = condicion.id
        else:
            condicion = Condiciones_operativas_cabecera.objects.filter(pk=condicion_id).first()
            if condicion:
                condicion.ctcondicion =ctcondicion
                condicion.laplicaafacturaspuras = aplica_facturaspuras_on
                condicion.laplicaaaccesorios = aplica_accesorios_on
                condicion.cxtipofactoring=tipo_factoring
                condicion.cxusuariomodifica = request.user.id
                condicion.save()
        
        if not condicion_id:
            return redirect("operaciones:listacondicionesoperativas")
        
        cxclasecliente=request.POST.get("cxclasecliente")
        cxclasecomprador=request.POST.get("cxclasecomprador")
        nplazodesde=request.POST.get("nplazodesde")
        nplazohasta=request.POST.get("nplazohasta")
        nporcentajeanticipo = request.POST.get("nporcentajeanticipo")
        ntasadescuento =request.POST.get("ntasadescuento")
        ntasagao =request.POST.get("ntasagao")
       
        clase_cliente = Clases_cliente.objects.filter(pk=cxclasecliente).first()
        clase_comprador = Clases_cliente.objects.filter(pk=cxclasecomprador).first()

        det = Condiciones_operativas_detalle(
            cxcondicion = condicion,
            cxclasecliente = clase_cliente,
            cxclasecomprador = clase_comprador,
            nplazodesde = nplazodesde,
            nplazohasta = nplazohasta,
            nporcentajeanticipo = nporcentajeanticipo,
            ntasadescuento = ntasadescuento,
            ntasagao = ntasagao,
            cxusuariocrea = request.user
        )

        if det:
            det.save()

        return redirect("operaciones:condicionesoperativas_editar", condicion_id = condicion_id)


    return render(request, template_name, contexto)

def DetalleCondicionOperativa(request, condicion_id = None):
    
    detalle = Condiciones_operativas_detalle.objects\
        .filter(cxcondicion=condicion_id)\
            .filter( leliminado = False)\
                .order_by('cxclasecliente', 'cxclasecomprador', 'nplazodesde')

    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    
    for i in range(len(detalle)):
        tempBlogs.append(CondicionesOperativasADictionario(detalle[i])) 

    docjson = tempBlogs

    data = {"total": detalle.count(),
        "totalNotFiltered": detalle.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def CondicionesOperativasADictionario(det):
    output = {}
    output['id'] = det.id
    output["ClaseCliente"] = det.cxclasecliente.cxclase
    output["ClaseComprador"] = det.cxclasecomprador.cxclase
    output["Desde"] = det.nplazodesde
    output["Hasta"] = det.nplazohasta
    output["Porc_Anticipo"] = det.nporcentajeanticipo
    output["Porc_GAO"] = det.ntasagao
    output["Porc_DC"] = det.ntasadescuento

    return output

@login_required(login_url='/login/')
@permission_required('operaciones.update_condiciones_operativas_detalle'
    , login_url='bases:sin_permisos')
def EliminarDetalleCondicionOperativa(request, detalle_id):
    # la eliminacion es lógica
    # debe devolver: 1 si esta bien, 0 si esta mal

    doc = Condiciones_operativas_detalle.objects.filter(pk=detalle_id).first()

    if not doc:
        return HttpResponse(0)

    if request.method=="GET":
        # marcar como eliminado
        doc.leliminado = True
        doc.cxusuarioelimina = request.user.id
        doc.save()

    return HttpResponse("OK")

def GenerarAnexos(request,asignacion_id):

    asignacion = Asignacion.objects.filter(pk=asignacion_id).first()
    
    cliente = Datos_participantes.objects\
        .filter(cxparticipante=asignacion.cxcliente.cxparticipante).first()
        
    anexos = Anexos.objects.filter(lactivo = True).all()

    if cliente.datos_generales.cxtipocliente =="J":
        datos = ModeloCliente.Personas_juridicas.objects\
            .filter(cxcliente = cliente).first()
        if datos:
            rl_id = datos.cxrepresentante1
            rl_nombre = datos.ctrepresentante1
    else:
        rl_id = cliente.cxparticipante
        rl_nombre = cliente.ctnombre
    
    for anexo in anexos:

        ruta_anexo_generado = anexo.ctrutageneracion
        ruta_plantilla = anexo.ctrutaanexo
        
        plantilla = DocxTemplate(ruta_plantilla)
        
        archivo = ruta_anexo_generado + anexo.ctnombre + ' DE ' \
            + cliente.ctnombre+"-" \
            + asignacion.cxasignacion+".docx"

        fecha_negociacion = asignacion.dnegociacion

        context = { 
            'direccion' : cliente.ctdireccion ,
            'fechanegociacion': fecha_negociacion.strftime("%Y-%B-%d"),
            'idcliente': cliente.cxparticipante,
            'idrepresentantelegal':rl_id,
            'maximoplazonegociacion':asignacion.nmayorplazonegociacion,
            'nombrecliente':cliente.ctnombre,
            'nombrerepresentantelegal':rl_nombre,
            'totalanticipo': asignacion.nanticipo,
            'totalanticipoenletras': numero_a_letras(asignacion.nanticipo),
            }
        plantilla.render(context)
        plantilla.save(archivo)
    
        # subprocess.run(["word.exe",archivo])

    return HttpResponse("Se han generado archivos en la carpeta correspondientes")

def ReversaAceptacionAsignacion(request, pid_asignacion):
    # # ejecuta un store procedure 
    resultado=enviarPost("CALL uspReversaAceptacionAsignacion( {0},'')"
    .format(pid_asignacion))

    return HttpResponse(resultado)

def GeneraListaAsignacionesJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    if desde == 'None':
        asignacion = Asignacion.objects.all().order_by('ddesembolso')
    else:
        asignacion = Asignacion.objects\
            .filter(ddesembolso__gte = desde, ddesembolso__lte = hasta)\
            .order_by('ddesembolso')
    tempBlogs = []
    for i in range(len(asignacion)):
        tempBlogs.append(GeneraListaAsignacionesJSONSalida(asignacion[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": asignacion.count(),
        "totalNotFiltered": asignacion.count(),
        "rows": docjson 
        }
    return JsonResponse( data)
    # prueba de bootstrap con filtro de columna
    # data = docjson         
    # return JsonResponse( data, safe=False)

def GeneraListaAsignacionesJSONSalida(asignacion):
    output = {}

    neto = asignacion.nanticipo - asignacion.ngao - asignacion.ndescuentodecartera - asignacion.niva
    output["id"] = asignacion.id
    output["Cliente"] = asignacion.cxcliente.ctnombre
    output["Asignacion"] = asignacion.cxasignacion
    output["TipoFactoring"] = asignacion.cxtipofactoring.cttipofactoring
    # output["TipoAsignacion"] = asignacion.cxtipo
    if asignacion.cxtipo =='F':
        output["TipoAsignacion"] = "Facturas puras"
    else:
        output["TipoAsignacion"] = "Con accesorios"
    output["FechaDesembolso"] = asignacion.ddesembolso.strftime("%Y-%m-%d")
    output["ValorNegociado"] =  asignacion.nvalor
    output["PlazoMayor"] = asignacion.nmayorplazonegociacion
    output["InstruccionDePago"] = asignacion.ctinstrucciondepago
    output["Cargos"] = asignacion.ngao + asignacion.ndescuentodecartera
    output["IVA"] = asignacion.niva
    output["Neto"] = neto
    output["Estado"] = asignacion.cxestado
    output["Registro"] = asignacion.dregistro

    return output

def GeneraListaAsignacionesRegistradasJSON(request, desde = None, hasta= None):
    # Es invocado desde la url de una tabla bt

    if desde == 'None':
        asignacion = Asignacion.objects.all()
    else:
        asignacion = Asignacion.objects\
            .filter(dregistro__gte = desde, dregistro__lte = hasta)
    tempBlogs = []
    for i in range(len(asignacion)):
        tempBlogs.append(GeneraListaAsignacionesJSONSalida(asignacion[i])) 

    docjson = tempBlogs

    # crear el contexto
    data = {"total": asignacion.count(),
        "totalNotFiltered": asignacion.count(),
        "rows": docjson 
        }
    return JsonResponse( data)

def GeneraListaAntigüedadCarteraJSON(request):
    # Es invocado desde la url de una tabla bt

    documentos = Documentos.objects.antigüedad_cartera()
        
    output = {}

    output["vencido_mas_90"] = documentos.vencido_mas_90
    output["vencido_90"] = documentos.vencido_90
    output["TipoFactoring"] = documentos.cxtipofactoring.cttipofactoring

    # crear el contexto
    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }
    return JsonResponse( data)
