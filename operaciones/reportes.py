import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from .models import Asignacion, Documentos, ChequesAccesorios
from cobranzas.models import Documentos_protestados
from django.shortcuts import render
from empresa.models import Tasas_factoring
from django.db.models import Sum, Count
from solicitudes import models as SolicitudModels

FACTURAS_PURAS = 'F'

def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        result = finders.find(uri)
        if result:
                if not isinstance(result, (list, tuple)):
                        result = [result]
                result = list(os.path.realpath(path) for path in result)
                path=result[0]
        else:
                sUrl = settings.STATIC_URL        # Typically /static/
                sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                mUrl = settings.MEDIA_URL         # Typically /media/
                mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                if uri.startswith(mUrl):
                        path = os.path.join(mRoot, uri.replace(mUrl, ""))
                elif uri.startswith(sUrl):
                        path = os.path.join(sRoot, uri.replace(sUrl, ""))
                else:
                        return uri

        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception(
                        'media URI must start with %s or %s' % (sUrl, mUrl)
                )
        return path

def ImpresionAsignacionDesdeSolicitud(request, asignacion_id):

        # tomar el codigo de asignacion grabado en la solicitud
        solicitud = SolicitudModels.Asignacion.objects.filter(id= asignacion_id).first()
        cliente_id = solicitud.cxcliente.cxcliente
        
        asgn = Asignacion.objects\
                .filter(id = solicitud.asignacion)\
                .filter(cxcliente_id = cliente_id).first()

        if asgn:
                return ImpresionAsignacion(request, asgn.id)
        else:   
                return HttpResponse("no encontró asignación ")

def ImpresionAsignacion(request, asignacion_id):
    asignacion = Asignacion.objects.filter(id = asignacion_id).first()
    documentos = {}

    if asignacion.cxtipo==FACTURAS_PURAS:
        template_path = 'operaciones/asignacion_facturas_puras_reporte.html'
        documentos = Documentos.objects.filter(cxasignacion = asignacion)\
                .filter(leliminado = False)
    else:
        template_path = 'operaciones/asignacion_facturas_accesorios_reporte.html'
        documentos = ChequesAccesorios.objects\
            .filter(leliminado = False, documento__in=Documentos.objects
            .filter(cxasignacion=asignacion_id))\
                .filter( leliminado = False)

    # datos de tasa gao/dc
    gao = Tasas_factoring.objects.filter(cxtasa="GAO").first()
    if not gao:
        return HttpResponse("no encontró tasa de gao en el sistema."
                +" Registre el cargo con código GAO")

    dc = Tasas_factoring.objects.filter(cxtasa="DCAR").first()
    if not dc:
        return HttpResponse("no encontró tasa de descuento de "
                +"catera en el sistema.Registre el cargo con código DCAR")

    dic_gao  = {'imprimir':gao.limprimeenreporte
        , 'descripcion': gao.ctdescripcionenreporte
        , 'iniciales': gao.ctinicialesentablas}
        
    dic_dc = {'imprimir':dc.limprimeenreporte
        , 'descripcion': dc.ctdescripcionenreporte
        , 'iniciales': dc.ctinicialesentablas}
    
    subtotal = asignacion.nanticipo - asignacion.ngao - asignacion.ndescuentodecartera
    neto = subtotal - asignacion.niva

    context = {
        "asignacion" : asignacion,
        "documentos" : documentos,
        'gao': dic_gao,
        'dc' : dic_dc,
        'subtotal': subtotal,
        'neto': neto,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="asgn"' + str(asignacion_id) + ".pdf"
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def ImpresionCartera(request, ):
    facturas = Documentos.objects.antigüedad_por_cliente()
    accesorios = ChequesAccesorios.objects.antigüedad_por_cliente()
    prot_facturas = Documentos_protestados.objects.antigüedad_por_cliente_facturas()
    prot_accesorios = Documentos_protestados.objects.antigüedad_por_cliente_accesorios()

    total_facturas = Documentos.objects.antigüedad_cartera()
    total_accesorios = ChequesAccesorios.objects.antigüedad_cartera()
    total_protestos = Documentos_protestados.objects.antigüedad_cartera()

    fvm90 = total_facturas['vencido_mas_90'] 
    fv90 = total_facturas['vencido_90']
    fv60 = total_facturas['vencido_60']
    fv30 = total_facturas['vencido_30']
    fx30 = total_facturas['porvencer_30']
    fx60 = total_facturas['porvencer_60']
    fx90 = total_facturas['porvencer_90']
    fxm90 = total_facturas['porvencer_mas_90']
    if not fvm90: fvm90=0
    if not fv90: fv90=0
    if not fv60: fv60=0
    if not fv30: fv30=0
    if not fx30: fx30=0
    if not fx60: fx60=0
    if not fx90: fx90=0
    if not fxm90: fxm90=0

    avm90 = total_accesorios['vencido_mas_90']
    av90 = total_accesorios['vencido_90']
    av60 = total_accesorios['vencido_60']
    av30 = total_accesorios['vencido_30']
    ax30 = total_accesorios['porvencer_30']
    ax60 = total_accesorios['porvencer_60']
    ax90 = total_accesorios['porvencer_90']
    axm90 = total_accesorios['porvencer_mas_90']
    if not avm90: avm90=0
    if not av90: av90 = 0
    if not av60: av60 = 0
    if not av30: av30 = 0
    if not ax30: ax30 = 0
    if not ax60: ax60 = 0
    if not ax90: ax90 = 0
    if not axm90: axm90 = 0

    pvm90 = total_protestos['vencido_mas_90']
    pv90 = total_protestos['vencido_90']
    pv60 = total_protestos['vencido_60']
    pv30 = total_protestos['vencido_30']
    px30 = total_protestos['porvencer_30']
    px60 = total_protestos['porvencer_60']
    px90 = total_protestos['porvencer_90']
    pxm90 = total_protestos['porvencer_mas_90']
    if not pvm90: pvm90=0
    if not pv90: pv90 = 0
    if not pv60: pv60 = 0
    if not pv30: pv30 = 0
    if not px30: px30 = 0
    if not px60: px60 = 0
    if not px90: px90 = 0
    if not pxm90: pxm90 = 0

    template_path = 'operaciones/cartera_reporte.html'

    context = {
        "documentos" : facturas.union(accesorios, prot_facturas, prot_accesorios),
        "totalvm90"  : fvm90+avm90+pvm90,
        "totalv90"   : fv90+av90+pv90,
        "totalv60"   : fv60+av60+pv60,
        "totalv30"   : fv30+av30+pv30,
        "totalx30"   : fx30+ax30+px30,
        "totalx60"   : fx60+ax60+px60,
        "totalx90"   : fx90+ax90+px90,
        "totalxm90"  : fxm90+axm90+pxm90,
        "total" : fvm90+fv90+fv60+fv30+avm90+av90+av60+av30+pvm90+pv90+pv60+pv30
                +fxm90+fx90+fx60+fx30+axm90+ax90+ax60+ax30+pxm90+px90+px60+px30
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="cartera.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def EstadoOperativoCliente(request, cliente_id):
    
    facturas = Documentos.objects.antigüedad_por_cliente()\
        .filter(cxcliente=cliente_id)
    accesorios = ChequesAccesorios.objects.antigüedad_por_cliente()\
        .filter(documento__cxcliente=cliente_id)

    template_path = 'operaciones/estadooperativo_reporte.html'
    context={
      'facturas':facturas
      ,'accesorios':accesorios
        }
    return render(request, template_path, context)

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="estado_operativo.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
