import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from .models import Asignacion, Documentos, ChequesAccesorios
from django.shortcuts import render
from empresa.models import Tasas_factoring
from django.db.models import Sum, Count
from solicitudes import models as SolicitudModels

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
                .filter(cxasignacion = solicitud.cxasignacion)\
                .filter(cxcliente_id = cliente_id).first()

        if asgn:
                return ImpresionAsignacion(request, asgn.id)
        else:   
                return HttpResponse("no encontró asignación ")

def ImpresionAsignacion(request, asignacion_id):
    asignacion = Asignacion.objects.filter(id = asignacion_id).first()
    documentos = {}

    if asignacion.cxtipo=="P":
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
        , 'descripcion': gao.ctdescripcionenreporte}
    dic_dc = {'imprimir':dc.limprimeenreporte
        , 'descripcion': dc.ctdescripcionenreporte}
    
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