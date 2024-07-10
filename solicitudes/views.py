from decimal import Decimal
from datetime import date
from pydoc import doc

from django.shortcuts import redirect, render
from django.views import generic
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.db import transaction
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
from datetime import datetime, timedelta

from .forms import AsignacionesForm, ChequesForm, DocumentosForm\
    , ClientesForm

from empresa.models import Tipos_factoring, Datos_participantes
from .models import Asignacion, ChequesAccesorios, Documentos, Clientes
from clientes.models import Datos_compradores
from pais.models import Bancos, Feriados
from bases.models import Usuario_empresa, Empresas

from bases.views import enviarPost, SinPrivilegios

import datetime
import json

FACTURAS_PURAS = 'F'
FACTURAS_CON_ACCESORIOS = 'A'
DIAS_PRUEBA_SISTEMA =60
# Create your views here.
class SolicitudesView(SinPrivilegios, generic.ListView):
    model = Asignacion
    template_name = "solicitudes/listasolicitudes.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    permission_required="solicitudes.view_asignacion"

    def get_queryset(self) :
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        qs=Asignacion.objects.filter(cxestado ='P',leliminado = False
                                     , empresa = id_empresa.empresa)\
                                     .order_by("dregistro")
        return qs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(SolicitudesView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class AsignacionFacturasPurasView(SinPrivilegios, generic.UpdateView):
    model = Asignacion
    template_name = "solicitudes/datosasignacionfacturaspuras_form.html"
    context_object_name='asignacion'
    login_url = 'bases:login'
    form_class = AsignacionesForm
    success_url=reverse_lazy("solicitudes:listasolicitudes")
    permission_required="solicitudes.change_asignacion"
    
    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(AsignacionFacturasPurasView, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(AsignacionFacturasPurasView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context
       
class AsignacionConAccesoriosView(SinPrivilegios, generic.UpdateView):
    model = Asignacion
    template_name = "solicitudes/datosasignacionconaccesorios_form.html"
    context_object_name='asignacion'
    login_url = 'bases:login'
    form_class = AsignacionesForm
    success_url=reverse_lazy("solicitudes:listasolicitudes")
    permission_required="solicitudes.change_asignacion"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(AsignacionConAccesoriosView, self).get_form_kwargs()
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        kwargs['empresa'] = id_empresa.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(AsignacionConAccesoriosView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

class ClienteCrearView(SinPrivilegios, generic.CreateView):
    model = Clientes
    template_name="solicitudes/datosclientes_form.html"
    context_object_name="cliente"
    login_url = "bases:login"
    form_class = ClientesForm
    success_url= reverse_lazy("solicitudes:listasolicitudes")
    permission_required="solicitudes.add_clientes"

    def form_valid(self, form):

        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        form.instance.empresa = id_empresa.empresa
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id_empresa = Usuario_empresa.objects.filter(user = self.request.user).first()
        context = super(ClienteCrearView, self).get_context_data(**kwargs)
        sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()
        context['solicitudes_pendientes'] = sp
        return context

@login_required(login_url='/login/')
@permission_required('solicitudes.change_asignacion', login_url='bases:sin_permisos')
def DatosAsignacionFacturasPurasNueva(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    template_name="solicitudes/datosasignacionfacturaspuras_form.html"
    
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                    empresa = id_empresa.empresa).count()

    contexto={'form': AsignacionesForm(empresa = id_empresa.empresa),
            'clientes' : Clientes.objects.all() ,
            "asignacion": Asignacion,
            'solicitudes_pendientes':sp
       }
    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('solicitudes.change_asignacion', login_url='bases:sin_permisos')
def DatosAsignacionConAccesoriosNueva(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    template_name="solicitudes/datosasignacionconaccesorios_form.html"
    
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

    contexto={'form': AsignacionesForm(empresa = id_empresa.empresa),
            'clientes' : Clientes.objects.all(),
            "asignacion": Asignacion,
            'solicitudes_pendientes':sp
       }
    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('solicitudes.change_asignacion', login_url='bases:sin_permisos')
def DatosFacturasPuras(request, cliente_id=None
    , tipo_factoring_id=None, asignacion_id=None, doc_id = None):

    template_name="solicitudes/datosasignacionfacturaspuras_modal.html"
    form_documento = DocumentosForm()
    acepta_vencimiento_en_feriado = False

    if request.method=='GET':
        
        if doc_id:
            detalle = Documentos.objects.filter(pk=doc_id).first()
            e = {
            'cxcomprador':detalle.cxcomprador
            , 'ctcomprador':detalle.ctcomprador
            , 'ctserie1':detalle.ctserie1
            , 'ctserie2':detalle.ctserie2
            ,'ctdocumento':detalle.ctdocumento
            , 'demision':date.isoformat(detalle.demision)
            , 'dvencimiento':date.isoformat(detalle.dvencimiento)
            , 'nvalorantesiva':detalle.nvalorantesiva
            , 'niva':detalle.niva
            , 'nretencioniva':detalle.nretencioniva
            , 'nretencionrenta':detalle.nretencionrenta
            , 'ntotal':detalle.ntotal
            , 'nvalornonegociado':detalle.nvalornonegociado
            }
            form_documento = DocumentosForm(e)

        if tipo_factoring_id:
            tipoFactoring = Tipos_factoring.objects.filter(pk=tipo_factoring_id).first()
            
            acepta_vencimiento_en_feriado = tipoFactoring.lpermitediasferiados

    contexto={'form_documento':form_documento,
        'cliente': cliente_id,
        'tipo_factoring': tipo_factoring_id,
        'asignacion_id': asignacion_id,
        'doc_id' : doc_id,
        'vencimiento_en_feriado':acepta_vencimiento_en_feriado
       }

    if request.method=='POST':

        id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
        
        tipoasignacion = FACTURAS_PURAS

        if not cliente_id:
            # cuando es nuevo no hay parametros, se toma del request
            cliente_id =request.POST.get("cliente_id")

        cliente = Clientes.objects.get(pk=cliente_id)

        if not tipo_factoring_id:
            tipo_factoring_id =request.POST.get("id_tipofactoring")

        tipoFactoring = Tipos_factoring.objects\
            .filter(pk=tipo_factoring_id).first()

        with transaction.atomic():

            if not asignacion_id:

                asignacion = Asignacion(
                    cxcliente = cliente,
                    cxtipofactoring = tipoFactoring,
                    cxtipo = tipoasignacion,
                    nvalor = 0,
                    ncantidaddocumentos = 0,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if asignacion:
                    asignacion.save()
                    asignacion_id = asignacion.id
            else:
                asignacion = Asignacion.objects.filter(pk= asignacion_id).first()
                if asignacion:

                    asignacion.cxcliente = cliente
                    asignacion.cxtipofactoring = tipoFactoring
                    asignacion.cxtipo = tipoasignacion
                    asignacion.cxusuariomodifica = request.user.id
                    asignacion.save()

            if not asignacion_id:
                return redirect("solicitudes:listasolicitudes")

            id_comprador=request.POST.get("cxcomprador")
            nombre_comprador=request.POST.get("ctcomprador")
            documento=request.POST.get("ctdocumento")
            emision =request.POST.get("demision")
            vencimiento =request.POST.get("dvencimiento")
            valor_antes_de_iva =request.POST.get("nvalorantesiva")
            iva =request.POST.get("niva")
            retencion_iva =request.POST.get("nretencioniva")
            retencion_renta =request.POST.get("nretencionrenta")
            total = request.POST.get("ntotal")
            valornonegociado = request.POST.get("nvalornonegociado")
            serie1=request.POST.get("ctserie1")
            serie2=request.POST.get("ctserie2")

            # segun tipo de factoring no acepte vencimientos en feriados
            # cambiar la fecha de vencimiento

            if not tipoFactoring.lpermitediasferiados:

                fecha = parse_date(vencimiento)
                
                while Feriados.objects.filter(dferiado = vencimiento)\
                    .filter(llaborable = False).first() \
                        or fecha.weekday()== 6 or fecha.weekday() == 5:
                        
                    fecha = parse_date(vencimiento)
                    fecha = fecha + datetime.timedelta(days=1)
                    vencimiento = date.isoformat(fecha)

            if not doc_id:
                detalle = Documentos(
                    cxasignacion=asignacion,
                    cxcomprador = id_comprador,
                    ctcomprador = nombre_comprador,
                    ctdocumento = documento,
                    demision  = emision,
                    dvencimiento  = vencimiento,
                    nvalorantesiva = valor_antes_de_iva,
                    niva = iva,
                    nretencioniva = retencion_iva,
                    nretencionrenta = retencion_renta,
                    ntotal = total,
                    nvalornonegociado = valornonegociado,
                    ctserie1 = serie1,
                    ctserie2 = serie2,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
            else:

                detalle = Documentos.objects.filter(pk=doc_id).first()

                detalle.cxcomprador = id_comprador
                detalle.ctcomprador = nombre_comprador
                detalle.ctdocumento = documento
                detalle.demision  = emision
                detalle.dvencimiento  = vencimiento
                detalle.nvalorantesiva = valor_antes_de_iva
                detalle.niva = iva
                detalle.nretencioniva = retencion_iva
                detalle.nretencionrenta = retencion_renta
                detalle.ntotal = total
                detalle.nvalornonegociado = valornonegociado
                detalle.ctserie1 = serie1
                detalle.ctserie2 = serie2
                detalle.cxusuariomodifica = request.user.id

            if detalle:
                detalle.save()

                total_factura = Documentos.objects.filter(cxasignacion=asignacion_id)\
                    .filter(leliminado=False).aggregate(Sum('ntotal'))
                numero_documentos = Documentos.objects.filter(cxasignacion=asignacion_id)\
                    .filter(leliminado=False).aggregate(Count('ctdocumento'))
                asignacion.nvalor = total_factura["ntotal__sum"]
                asignacion.ncantidaddocumentos = numero_documentos["ctdocumento__count"]
                asignacion.save()

            # grabar comprador , si es nuevo
            datosparticipante = Datos_participantes.objects\
                .filter(cxparticipante = id_comprador
                        , empresa = id_empresa.empresa).first()
            if not datosparticipante:

                cxtipoid = request.POST.get("cxtipoid")

                datosparticipante=Datos_participantes(
                    cxtipoid=cxtipoid,
                    cxparticipante=id_comprador,
                    ctnombre=nombre_comprador,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if datosparticipante:
                    datosparticipante.save()

            comprador = Datos_compradores.objects\
                .filter(cxcomprador = datosparticipante.id).first()

            if not comprador:
                datoscomprador=Datos_compradores(
                    cxcomprador = datosparticipante,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa
                )
                if datoscomprador:
                    datoscomprador.save()

            # grabar fecha de inicio de operaciones
            factor = Empresas.objects.filter(pk = id_empresa.empresa.id).first()
            if not factor.diniciooperaciones:
                factor.diniciooperaciones = datetime.datetime.today()
                if factor.lgratis:
                    fin = datetime.datetime.today()+timedelta(days=DIAS_PRUEBA_SISTEMA)
                    factor.dfinpruebas = fin
                factor.save()

        return redirect("solicitudes:asignacionfacturaspuras_editar"
                        , pk= asignacion_id, )

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('solicitudes.change_documentos', login_url='bases:sin_permisos')
def EliminarDocumento(request, asignacion_id, documento_id, tipo_asignacion):
    # la eliminacion es lógica
    # el documento_id debe ser el id del accesorio cuando es asignacin con accesorios
    # el valor no negociado se encuentra en el total del documento, no debe restar adicional

    if request.method=="GET":
        # marcar como eliminado el doc o el cheque

        with transaction.atomic():
            asignacion = Asignacion.objects.filter(pk=asignacion_id).first()

            # cambiar P por F(acturas puras)
            # if tipo_asignacion=="P":
            if tipo_asignacion==FACTURAS_PURAS:
                doc = Documentos.objects.filter(pk=documento_id).first()
            else:
                # si es cheque actualizar el valor no negociado del documento
                # si es un solo cheque, eliminar la factura
                doc = ChequesAccesorios.objects.filter(pk = documento_id).first()
                factura =  Documentos.objects.filter(pk=doc.documento.id).first()

                factura.nvalornonegociado += doc.ntotal
                factura.ntotal -= doc.ntotal
                if factura.ntotal == 0:
                    factura.leliminado = True
                    factura.cxusuarioelimina = request.user.id
                factura.save()

            doc.leliminado = True
            doc.cxusuarioelimina = request.user.id
            doc.save()

            # actualizar la asignacion
            total_facturas = Documentos.objects.filter(cxasignacion=asignacion_id \
                , leliminado=False).aggregate(Sum('ntotal'))
            # total_nonegociado = Documentos.objects.filter(cxasignacion=asignacion_id \
            #     , leliminado=False).aggregate(Sum('nvalornonegociado'))
            numero_documentos = Documentos.objects.filter(cxasignacion=asignacion_id\
                , leliminado=False).aggregate(Count('ctdocumento'))
            
            total = total_facturas["ntotal__sum"] 
            # nonegociado = total_nonegociado["nvalornonegociado__sum"]
            cantidad = numero_documentos["ctdocumento__count"]

            if not total: 
                total = 0
                cantidad = 0
            # if not nonegociado:
            #     nonegociado=0

            if numero_documentos:
                asignacion.nvalor = total #- nonegociado
                asignacion.ncantidaddocumentos = cantidad
            else:
                asignacion.nvalor = 0
                asignacion.ncantidaddocumentos = 0

            asignacion.save()

    return HttpResponse("OK")

@login_required(login_url='/login/')
@permission_required('solicitudes.change_documentos', login_url='bases:sin_permisos')
def EliminarAsignacion(request, asignacion_id):
    # la eliminacion es lógica
    # debe devolver: 1 si esta bien, 0 si esta mal

    asgn = Asignacion.objects.filter(pk=asignacion_id).first()

    if not asgn:
        return HttpResponse(0)

    if request.method=="GET":
        # marcar como eliminado/ rechazada
        # asgn.leliminado = True
        # asgn.cxusuarioelimina = request.user.id
        asgn.cxusuarioatencion = request.user.id
        asgn.cxestado = "R"
        asgn.save()

    return HttpResponse("OK")

from django.http import JsonResponse
from . import models

def DetalleSolicitudFacturasPurasOutput(doc):
    output = {}
    output['id'] = doc.id
    output["Comprador"] = doc.ctcomprador
    output["Documento"] = doc.ctdocumento
    output["Emision"] = doc.demision.strftime("%Y-%m-%d")
    output["Vencimiento"] = doc.dvencimiento.strftime("%Y-%m-%d")
    output["ValorAntesDeIVA"] = doc.nvalorantesiva
    output["IVA"] = doc.niva
    output["Retenciones"] = doc.nretencioniva +doc.nretencionrenta
    output["NoNegociado"] = doc.nvalornonegociado
    output["Total"] = doc.ntotal

    return output

def DetalleSolicitudFacturasPuras(request, asignacion_id = None):
    
    documentos = models.Documentos.objects\
        .filter(cxasignacion=asignacion_id)\
            .filter( leliminado = False)
    
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(documentos)):
        tempBlogs.append(DetalleSolicitudFacturasPurasOutput(documentos[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DetalleSolicitudConAccesorios(request, asignacion_id = None):
    
    documentos = models.ChequesAccesorios.objects\
        .filter(documento__in=models.Documentos.objects\
            .filter(cxasignacion=asignacion_id, leliminado = False))\
            .filter( leliminado = False)
    
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(documentos)):
        tempBlogs.append(DetalleSolicitudConAccesoriosOuput(documentos[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": documentos.count(),
        "totalNotFiltered": documentos.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DetalleSolicitudConAccesoriosOuput(doc):
    output = {}
    # se va a mostrar id de accesorio para borrar el cheque y no la factura
    # output['id'] = str(doc.documento.id)
    output['id'] = str(doc.id)
    output["Comprador"] = doc.documento.ctcomprador
    output["Documento"] = doc.documento.ctdocumento
    output["Emision"] = doc.documento.demision.strftime("%Y-%m-%d")
    output["Banco"] = doc.cxbanco.ctbanco
    output["Cuenta"] = doc.ctcuenta
    output["Cheque"] = doc.ctcheque
    output["Vencimiento"] = doc.dvencimiento.strftime("%Y-%m-%d")
    output["Total"] = doc.ntotal

    return output

@login_required(login_url='/login/')
@permission_required('solicitudes.change_chequesaccesorios', login_url='bases:sin_permisos')
def DatosAsignacionConAccesorios(request, cliente_id=None, tipo_factoring_id=None
    , asignacion_id=None):
    template_name="solicitudes/datosdocumentosconaccesorios_form.html"
    formulario = {}
    asignacion = {}
    
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    if request.method=='GET':

        asignacion = Asignacion.objects.filter(pk=asignacion_id).first()

        if asignacion:
            e={
                'cxcliente': asignacion.cxcliente,
                'cxtipofactoring': asignacion.cxtipofactoring,
                'cxtipo': asignacion.cxtipo,
                'nvalor': asignacion.nvalor,
                'ncantidaddocumentos':asignacion.ncantidaddocumentos
            }
            formulario = AsignacionesForm(e)
        else:
            formulario=AsignacionesForm()
            asignacion=None
            
    # aunque se envía el form de cheques, el mismo no se utliza con submit
    # por lo que no se validan los campos pero sirve para la lista 
    
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

    contexto={'form_asignacion':formulario,
        'form_documento':DocumentosForm,
        # 'form_cheque': ChequesForm(),
        'asignacion' : asignacion,
        'asignacion_id': asignacion_id,
        'cliente': cliente_id,
        'tipo_factoring': tipo_factoring_id,
        'solicitudes_pendientes':sp
       }

    if request.method=='POST':

        idcliente = request.POST.get("id_cliente")
        tipo_factoring = request.POST.get("id_tipofactoring")
        tipoasignacion = FACTURAS_CON_ACCESORIOS

        cliente = Clientes.objects.get(pk=idcliente)

        tipoFactoring = Tipos_factoring.objects\
            .filter(pk=tipo_factoring).first()

        # inicio de transaccion
        with transaction.atomic():
            # crear la asignacion
            if not asignacion_id:

                asignacion = Asignacion(
                    cxcliente = cliente,
                    cxtipofactoring = tipoFactoring,
                    cxtipo = tipoasignacion,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if asignacion:
                    asignacion.save()
                    asignacion_id = asignacion.id

                # nueva = True
            else:
                asignacion = Asignacion.objects.filter(pk= asignacion_id).first()
                if asignacion:

                    asignacion.cxcliente = cliente
                    asignacion.cxtipofactoring = tipoFactoring
                    asignacion.cxtipo = tipoasignacion
                    asignacion.cxusuariomodifica = request.user.id
                    asignacion.save()

                # nueva = False

            if not asignacion_id:
                return redirect("solicitudes:listasolicitudes")

            id_comprador=request.POST.get("cxcomprador")
            nombre_comprador=request.POST.get("ctcomprador")
            documento=request.POST.get("ctdocumento")
            emision =request.POST.get("demision")
            # la factura no tiene fecha de vencimiento ya que eso está 
            # en los cheques. Este campo no debe ser utilizado
            vencimiento =request.POST.get("demision")
            valor_antes_de_iva =request.POST.get("nvalorantesiva")
            iva =request.POST.get("niva")
            retencion_iva =request.POST.get("nretencioniva")
            retencion_renta =request.POST.get("nretencionrenta")
            total = request.POST.get("ntotal")
            valornonegociado = request.POST.get("nvalornonegociado")
            serie1=request.POST.get("ctserie1")
            serie2=request.POST.get("ctserie2")

            det = Documentos(
                cxasignacion=asignacion,
                cxcomprador = id_comprador,
                ctcomprador = nombre_comprador,
                ctdocumento = documento,
                demision  = emision,
                dvencimiento  = vencimiento,
                nvalorantesiva = valor_antes_de_iva,
                niva = iva,
                nretencioniva = retencion_iva,
                nretencionrenta = retencion_renta,
                ntotal = total,
                nvalornonegociado = valornonegociado,
                ctserie1 = serie1,
                ctserie2 = serie2,
                cxusuariocrea = request.user,
                empresa = id_empresa.empresa,
            )

            if det:
                det.save()

                total_factura = Documentos.objects.filter(cxasignacion=asignacion_id)\
                    .filter(leliminado=False).aggregate(Sum('ntotal'))
                numero_documentos = Documentos.objects.filter(cxasignacion=asignacion_id)\
                    .filter(leliminado=False).aggregate(Count('ctdocumento'))
                asignacion.nvalor = total_factura["ntotal__sum"]
                asignacion.ncantidaddocumentos = numero_documentos["ctdocumento__count"]
                asignacion.save()

            # grabar comprador , si es nuevo
            datosparticipante = Datos_participantes.objects\
                .filter(cxparticipante = id_comprador
                        , empresa = id_empresa.empresa).first()
            
            if not datosparticipante:

                cxtipoid = request.POST.get("cxtipoid")

                datosparticipante=Datos_participantes(
                    cxtipoid=cxtipoid,
                    cxparticipante=id_comprador,
                    ctnombre=nombre_comprador,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if datosparticipante:
                    datosparticipante.save()

            comprador = Datos_compradores.objects\
                .filter(cxcomprador = datosparticipante.id).first()

            if not comprador:
                datoscomprador=Datos_compradores(
                    cxcomprador = datosparticipante,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if datoscomprador:
                    datoscomprador.save()

            # grabar detalle de cheques

            # recuperar el string de lista de cheques pasado en la data y
            # convertir a lista
            lista = request.POST.get("Cheques")
            output = eval(lista)

            for elem in output:      
                #accedemos a cada elemento de la lista (en este caso cada elemento es un dictionario)
                bco = Bancos.objects.filter(id = elem.get("banco")).first()

                vencimiento = elem.get("vencimiento")
                
                # segun tipo de factoring no acepte vencimientos en feriados
                # cambiar la fecha de vencimiento
                if not tipoFactoring.lpermitediasferiados:

                    fecha = parse_date(vencimiento)
                    
                    while Feriados.objects.filter(dferiado = vencimiento)\
                        .filter(llaborable = False).first() \
                            or fecha.weekday()== 6 or fecha.weekday() == 5:
                            
                        fecha = parse_date(vencimiento)
                        fecha = fecha + datetime.timedelta(days=1)
                        vencimiento = date.isoformat(fecha)

                cheque = ChequesAccesorios(
                    documento = det,
                    cxbanco=bco,
                    ctcuenta = elem.get("cuenta"),
                    ctcheque = elem.get("cheque"),
                    ctgirador = elem.get("girador"),
                    dvencimiento = vencimiento,
                    ntotal = elem.get("valor"),
                    cxusuariocrea = request.user,
                    cxpropietariocuenta = elem.get("propietariocuenta"),
                    empresa = id_empresa.empresa,
                )
                if cheque:
                    cheque.save()

        # la ejecucion de esta vista POST se hace por jquery.ajax 
        # y ese proceso traslada a la forma de edición de la 
        # asignación que se está creando o modificando
        return HttpResponse( asignacion_id)

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('solicitudes.change_chequesaccesorios', login_url='bases:sin_permisos')
def DatosAccesorioEditar(request, accesorio_id = None, tipo_factoring_id = None):

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    
    template_name = "solicitudes/datoschequeaccesorio_modal.html"
    form_cheque = ChequesForm(empresa=id_empresa.empresa)
    valor_cheque = None
    acepta_vencimiento_en_feriado = False
    
    if request.method=='GET':
        if accesorio_id:
            accesorio = ChequesAccesorios.objects.get(id=accesorio_id)
            e = {'documento':accesorio.documento
                , 'cxbanco':accesorio.cxbanco
                , 'ctcuenta':accesorio.ctcuenta
                , 'ctcheque':accesorio.ctcheque
                , 'ctgirador':accesorio.ctgirador
                , 'ntotal':accesorio.ntotal
                , 'dvencimiento':accesorio.dvencimiento
                , 'cxpropietariocuenta': accesorio.cxpropietariocuenta}
            form_cheque = ChequesForm(e, empresa=id_empresa.empresa)
            valor_cheque=accesorio.ntotal

        if tipo_factoring_id:
            tipoFactoring = Tipos_factoring.objects\
            .filter(pk=tipo_factoring_id).first()

            acepta_vencimiento_en_feriado = tipoFactoring.lpermitediasferiados
            
    contexto={'form_cheque': form_cheque,
        'cheque':accesorio_id,
        'valor': valor_cheque,
        'tipo_factoring':tipo_factoring_id,
        'vencimiento_en_feriado':acepta_vencimiento_en_feriado
}

    if request.method=='POST':

        if accesorio_id:
            banco = request.POST.get('cxbanco')
            cuenta = request.POST.get('ctcuenta')
            cheque = request.POST.get('ctcheque')
            girador = request.POST.get('ctgirador')
            vencimiento = request.POST.get('dvencimiento')
            propietario = request.POST.get('cxpropietariocuenta')

            accesorio = ChequesAccesorios.objects.get(id=accesorio_id)

            asg_id = accesorio.documento.cxasignacion.id
            tipo_factoring_id = accesorio.documento.cxasignacion\
                .cxtipofactoring.id
            
            tipoFactoring = Tipos_factoring.objects\
                .filter(pk=tipo_factoring_id).first()

            # segun tipo de factoring no acepte vencimientos en feriados
            # cambiar la fecha de vencimiento
            if not tipoFactoring.lpermitediasferiados:

                fecha = parse_date(vencimiento)
                
                while Feriados.objects.filter(dferiado = vencimiento)\
                    .filter(llaborable = False).first() \
                        or fecha.weekday()== 6 or fecha.weekday() == 5:
                        
                    fecha = parse_date(vencimiento)
                    fecha = fecha + datetime.timedelta(days=1)
                    vencimiento = date.isoformat(fecha)

            bco = Bancos.objects.filter(pk=banco).first()

            accesorio.cxbanco = bco
            accesorio.ctcuenta = cuenta
            accesorio.ctcheque = cheque
            accesorio.ctgirador = girador
            accesorio.dvencimiento = vencimiento
            accesorio.cxpropietariocuenta = propietario

            accesorio.save()

        return redirect("solicitudes:asignacionconaccesorios_editar", pk= asg_id)

    return render(request, template_name, contexto)

def PedirArchivoXML(request):
    template_name = "solicitudes/importarasignacion_modal.html"
    return render(request, template_name)
from django.http import JsonResponse
from django.db import DataError

def ImportarOperacion(request):
    objeto=json.loads(request.body.decode("utf-8"))
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    id_cliente=objeto["id_cliente"]
    nombre_cliente=objeto["nombre_cliente"]
    tipo_factoring=objeto["tipo_factoring"]
    tipo_operacion=objeto["tipo_operacion"]
    numero_documentos=objeto["numero_documentos"]
    total_negociado=objeto["total_negociado"]
    documentos=objeto["documentos"]

    # buscar el tipo de factoring para condiciones
    tipoFactoring = Tipos_factoring.objects\
        .filter(ctabreviacion=tipo_factoring, empresa = id_empresa.empresa).first()
    
    if not tipoFactoring:
        return HttpResponse("Tipo de factoring no encontrado. Use los nombres abreviados de tipos de factoring", status=400)
                
    with transaction.atomic():
        try:
            # Intenta realizar operaciones de base de datos aquí
            # Por ejemplo, guardar un objeto que podría exceder el largo máximo permitido para un campo
            # grabar el cliente
            cliente = Clientes.objects.filter(cxcliente=id_cliente).first()
            if not cliente:
                cliente = Clientes(
                    cxcliente = id_cliente,
                    ctnombre = nombre_cliente,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )
                if cliente:
                    cliente.save()

            # grabar la asignacion
            asignacion = Asignacion(
                cxcliente = cliente,
                cxtipofactoring = tipoFactoring,
                cxtipo = tipo_operacion,
                nvalor = total_negociado,
                ncantidaddocumentos = numero_documentos,
                cxusuariocrea = request.user,
                empresa = id_empresa.empresa,
            )
            if asignacion:
                asignacion.save()
                asignacion_id = asignacion.id

            # grabar los documentos
            for doc in documentos:
                id_comprador=doc["ruc_comprador"]
                nombre_comprador=doc["nombre_comprador"]
                emision =doc["emision"]
                serie1=doc["serie1"]
                serie2=doc["serie2"]
                documento=doc["numero_documento"]
                vencimiento =doc["vencimiento"]
                valor_antes_de_iva =doc["valor_antes_iva"]
                iva =doc["valor_iva"]
                retencion_iva =doc["retencion_iva"]
                retencion_renta =doc["retencion_renta"]
                total = doc["total"]

                # segun tipo de factoring no acepte vencimientos en feriados
                # cambiar la fecha de vencimiento

                if not tipoFactoring.lpermitediasferiados:

                    fecha = parse_date(vencimiento)
                    
                    while Feriados.objects.filter(dferiado = vencimiento)\
                        .filter(llaborable = False).first() \
                            or fecha.weekday()== 6 or fecha.weekday() == 5:
                            
                        fecha = parse_date(vencimiento)
                        fecha = fecha + datetime.timedelta(days=1)
                        vencimiento = date.isoformat(fecha)

                detalle = Documentos(
                    cxasignacion=asignacion,
                    cxcomprador = id_comprador,
                    ctcomprador = nombre_comprador,
                    ctdocumento = documento,
                    demision  = emision,
                    dvencimiento  = vencimiento,
                    nvalorantesiva = valor_antes_de_iva,
                    niva = iva,
                    nretencioniva = retencion_iva,
                    nretencionrenta = retencion_renta,
                    ntotal = total,
                    ctserie1 = serie1,
                    ctserie2 = serie2,
                    cxusuariocrea = request.user,
                    empresa = id_empresa.empresa,
                )

                if detalle:
                    detalle.save()

                # grabar comprador , si es nuevo
                datosparticipante = Datos_participantes.objects\
                    .filter(cxparticipante = id_comprador
                            , empresa = id_empresa.empresa).first()
                if not datosparticipante:

                    cxtipoid = doc["tipo_id_comprador"]

                    datosparticipante=Datos_participantes(
                        cxtipoid=cxtipoid,
                        cxparticipante=id_comprador,
                        ctnombre=nombre_comprador,
                        cxusuariocrea = request.user,
                        empresa = id_empresa.empresa,
                    )
                    if datosparticipante:
                        datosparticipante.save()

                comprador = Datos_compradores.objects\
                    .filter(cxcomprador = datosparticipante.id).first()

                if not comprador:
                    datoscomprador=Datos_compradores(
                        cxcomprador = datosparticipante,
                        cxusuariocrea = request.user,
                        empresa = id_empresa.empresa
                    )
                    if datoscomprador:
                        datoscomprador.save()

            # grabar fecha de inicio de operaciones
            factor = Empresas.objects.filter(pk = id_empresa.empresa.id).first()
            if not factor.diniciooperaciones:
                factor.diniciooperaciones = datetime.datetime.today()
                if factor.lgratis:
                    fin = datetime.datetime.today()+timedelta(days=DIAS_PRUEBA_SISTEMA)
                    factor.dfinpruebas = fin
                factor.save()

        except DataError as e:
            error_message = str(e)
            # Captura errores específicos de la base de datos, como el exceso en el largo del dato
            return HttpResponse( error_message + '. Por favor, verifica y vuelve a intentarlo.', status=400)
        except Exception as e:
            error_message = str(e)
            # Captura otros errores generales
            return HttpResponse('Ha ocurrido un error inesperado: ' + error_message, status=500)

        return HttpResponse("OK"+str(asignacion_id))

