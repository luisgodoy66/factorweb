from decimal import Decimal
from datetime import date
from pydoc import doc

from django.shortcuts import redirect, render, get_object_or_404
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
DIAS_PRUEBA_SISTEMA =30
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
def DatosFacturasPuras(request, cliente_id, tipo_factoring_id
                       , asignacion_id=None, doc_id = None):

    template_name="solicitudes/datosasignacionfacturaspuras_modal.html"
    acepta_vencimiento_en_feriado = False

    tipoFactoring = Tipos_factoring.objects.filter(pk=tipo_factoring_id).first()        
    acepta_vencimiento_en_feriado = tipoFactoring.lpermitediasferiados

    if doc_id:
       detalle = get_object_or_404(Documentos, pk=doc_id)
    else:
        detalle = None

    if request.method=='GET':
        form_documento = DocumentosForm(instance=detalle)
        
    if request.method=='POST':

        # buscar el RUC para la validacion de la autorizacion del SRI
        cliente = Clientes.objects.get(pk=cliente_id)
        ruc = cliente.cxcliente

        form_documento = DocumentosForm(request.POST, instance = detalle, ruc=ruc)

        if form_documento.is_valid():

            id_empresa = Usuario_empresa.objects\
                .filter(user = request.user).first()
            
            tipoasignacion = FACTURAS_PURAS

            with transaction.atomic():

                # crear la asignacion
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

                # grabar detalle de factura
                detalle = form_documento.save(commit=False)

                detalle.cxasignacion = asignacion
                detalle.empresa = id_empresa.empresa
                if not doc_id:
                    detalle.cxusuariocrea = request.user
                else:
                    detalle.cxusuariomodifica = request.user.id

                if not tipoFactoring.lpermitediasferiados:
                    vencimiento =form_documento.cleaned_data.get("dvencimiento")

                    # fecha = parse_date(vencimiento)
                    fecha = vencimiento
                    
                    while Feriados.objects.filter(dferiado = vencimiento)\
                        .filter(llaborable = False).first() \
                            or fecha.weekday()== 6 or fecha.weekday() == 5:
                            
                        # fecha = parse_date(vencimiento)
                        fecha = vencimiento
                        fecha = fecha + datetime.timedelta(days=1)
                        # vencimiento = date.isoformat(fecha)
                        vencimiento = fecha

                    detalle.dvencimiento = vencimiento

                detalle.save()

                # actualizar la asignacion
                total_factura = Documentos.objects.filter(cxasignacion=asignacion_id)\
                    .filter(leliminado=False).aggregate(Sum('ntotal'))
                numero_documentos = Documentos.objects.filter(cxasignacion=asignacion_id)\
                    .filter(leliminado=False).aggregate(Count('ctdocumento'))
                asignacion.nvalor = total_factura["ntotal__sum"]
                asignacion.ncantidaddocumentos = numero_documentos["ctdocumento__count"]
                asignacion.save()

                # grabar comprador , si es nuevo
                datosparticipante = Datos_participantes.objects\
                    .filter(cxparticipante = form_documento.cleaned_data.get("cxcomprador")
                            , empresa = id_empresa.empresa).first()
                if not datosparticipante:

                    cxtipoid = request.POST.get("cxtipoid")

                    datosparticipante=Datos_participantes(
                        cxtipoid = cxtipoid,
                        cxparticipante = form_documento.cleaned_data.get("cxcomprador"),
                        ctnombre = form_documento.cleaned_data.get("ctcomprador"),
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
                # factor = Empresas.objects.filter(pk = id_empresa.empresa.id).first()
                factor = id_empresa.empresa
                if not factor.diniciooperaciones:
                    factor.diniciooperaciones = datetime.datetime.today()
                    if factor.lgratis:
                        fin = datetime.datetime.today()+timedelta(days=DIAS_PRUEBA_SISTEMA)
                        factor.dfinpruebas = fin
                    factor.save()

            return HttpResponse( asignacion_id)
            # return redirect("solicitudes:asignacionfacturaspuras_editar"
            #                 , pk= asignacion_id, )
        else:
            return JsonResponse(form_documento.errors, status=400)
        
    contexto={'form_documento':form_documento,
        'cliente': cliente_id,
        'tipo_factoring': tipo_factoring_id,
        'asignacion_id': asignacion_id,
        'doc_id' : doc_id,
        'vencimiento_en_feriado':acepta_vencimiento_en_feriado
       }

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
            numero_documentos = Documentos.objects.filter(cxasignacion=asignacion_id\
                , leliminado=False).aggregate(Count('ctdocumento'))
            
            asignacion.nvalor =  total_facturas["ntotal__sum"] or 0
            asignacion.ncantidaddocumentos = numero_documentos["ctdocumento__count"] or 0

            asignacion.save()

    return HttpResponse("OK")

@login_required(login_url='/login/')
@permission_required('solicitudes.change_documentos', login_url='bases:sin_permisos')
def RecuperarDocumento(request, asignacion_id, documento_id, tipo_asignacion):
    # la eliminacion es lógica
    # el documento_id debe ser el id del accesorio cuando es asignacin con accesorios
    # el valor no negociado se encuentra en el total del documento, no debe restar adicional

    if request.method=="GET":
        # marcar como eliminado el doc o el cheque

        with transaction.atomic():
            asignacion = Asignacion.objects.filter(pk=asignacion_id).first()

            if tipo_asignacion==FACTURAS_PURAS:
                doc = Documentos.objects.filter(pk=documento_id).first()
            else:
                # si es cheque actualizar el valor no negociado del documento
                # si es un solo cheque, eliminar la factura
                doc = ChequesAccesorios.objects.filter(pk = documento_id).first()
                factura =  Documentos.objects.filter(pk=doc.documento.id).first()

                factura.nvalornonegociado -= doc.ntotal
                factura.ntotal += doc.ntotal
                if factura.leliminado:
                    factura.leliminado = False
                    # factura.cxusuarioelimina = request.user.id
                factura.save()

            doc.leliminado = False
            # doc.cxusuarioelimina = request.user.id
            doc.save()

            # actualizar la asignacion
            total_facturas = Documentos.objects.filter(cxasignacion=asignacion_id \
                , leliminado=False).aggregate(Sum('ntotal'))
            numero_documentos = Documentos.objects.filter(cxasignacion=asignacion_id\
                , leliminado=False).aggregate(Count('ctdocumento'))
            
            asignacion.nvalor =  total_facturas["ntotal__sum"] or 0
            asignacion.ncantidaddocumentos = numero_documentos["ctdocumento__count"] or 0

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
    # mostrar incluso los documentos eliminados
    documentos = models.ChequesAccesorios.objects\
        .filter(documento__in=models.Documentos.objects\
            .filter(cxasignacion=asignacion_id
                    # , leliminado = False
                    ))\
            # .filter( leliminado = False)
    
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
    output["Eliminado"] = doc.leliminado

    return output

@login_required(login_url='/login/')
@permission_required('solicitudes.change_chequesaccesorios', login_url='bases:sin_permisos')
def DatosAsignacionConAccesorios(request, cliente_id, 
                                 tipo_factoring_id=None, 
                                 asignacion_id=None, 
                                 cliente_nombre=None):
    # aca sólo se crea el documento, no se modifica.
    template_name="solicitudes/datosdocumentosconaccesorios_form.html"
    asignacion = {}
    contexto = {}
    form_documento = {}
    id_empresa = Usuario_empresa.objects\
        .filter(user = request.user).first()
    
    asignacion = Asignacion.objects\
        .filter(pk=asignacion_id).first()

    if asignacion:
        cliente_nombre = asignacion.cxcliente.ctnombre
    
    sp = Asignacion.objects.filter(cxestado='P', leliminado=False,
                                       empresa = id_empresa.empresa).count()

    if request.method=='POST':

        tipoasignacion = FACTURAS_CON_ACCESORIOS

        tipoFactoring = Tipos_factoring.objects\
            .get(pk=tipo_factoring_id)

        cliente = Clientes.objects.get(pk=cliente_id)
        ruc = cliente.cxcliente

        form_documento = DocumentosForm(request.POST, ruc=ruc)

        if form_documento.is_valid():
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

                det = form_documento.save(commit=False)
                det.cxasignacion = asignacion
                det.empresa = id_empresa.empresa
                det.cxusuariocrea = request.user
                det.dvencimiento = form_documento.cleaned_data.get("demision")
                # if det:
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
                    .filter(cxparticipante = form_documento.cleaned_data.get("cxcomprador")
                            , empresa = id_empresa.empresa).first()
                
                if not datosparticipante:

                    cxtipoid = request.POST.get("cxtipoid")

                    datosparticipante=Datos_participantes(
                        cxtipoid=cxtipoid,
                        cxparticipante=form_documento.cleaned_data.get("cxcomprador"),
                        ctnombre=form_documento.cleaned_data.get("ctcomprador"),
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

            return HttpResponse( asignacion_id)
        else:
            return JsonResponse(form_documento.errors, status=400)
    else:
        form_documento = DocumentosForm()

    contexto.update({
        'form_documento':form_documento,
        'asignacion_id': asignacion_id,
        'cliente': cliente_id,
        'tipo_factoring': tipo_factoring_id,
        'solicitudes_pendientes':sp,
        'cliente_nombre':cliente_nombre,
       })

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
                if doc:
                    id_comprador = doc.get("ruc_comprador", None)
                    nombre_comprador = doc.get("nombre_comprador", None)
                    emision = doc.get("emision", None)
                    serie1 = doc.get("serie1", "")
                    serie2 = doc.get("serie2", "")
                    documento = doc.get("numero_documento", "")
                    vencimiento = doc.get("vencimiento", None)
                    valor_antes_de_iva = doc.get("valor_antes_iva", 0)
                    iva = doc.get("valor_iva", 0)
                    retencion_iva = doc.get("retencion_iva", 0)
                    retencion_renta = doc.get("retencion_renta", 0)
                    total = doc.get("total", 0)
                    no_negociado = doc.get("descartar", 0)

                    # si el id del comprador no existe, descartar el documento
                    if not id_comprador or not nombre_comprador or not emision \
                        or not vencimiento or total == 0:
                        continue

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
                        nvalornonegociado = no_negociado,
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

