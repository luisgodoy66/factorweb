import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from .models import Asignacion, Documentos, ChequesAccesorios, Cheques_quitados
from cobranzas.models import Documentos_protestados
from django.shortcuts import render
from empresa.models import Tasas_factoring
from django.db.models import Sum, Count
from solicitudes import models as SolicitudModels
from bases.models import Usuario_empresa

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

        solicitud = SolicitudModels.Asignacion.objects.filter(id= asignacion_id).first()
        
        asgn = Asignacion.objects\
                .filter(id = solicitud.asignacion).first()

        if asgn:
                return ImpresionAsignacion(request, asgn.id)
        else:   
                return HttpResponse("no encontró asignación ")

def ImpresionAsignacion(request, asignacion_id):
    asignacion = Asignacion.objects.filter(id = asignacion_id).first()
    documentos = {}

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    if asignacion.cxtipo==FACTURAS_PURAS:
        template_path = 'operaciones/asignacion_facturas_puras_reporte.html'
        documentos = Documentos.objects.filter(cxasignacion = asignacion)\
                .filter(leliminado = False)
    else:
        template_path = 'operaciones/asignacion_facturas_accesorios_reporte.html'
        documentos = ChequesAccesorios.objects\
            .filter(leliminado = False
                    , ncanjeadopor = None
                    , documento__in=Documentos.objects.filter(cxasignacion=asignacion_id))\
                .filter( leliminado = False)

    # datos de tasa gao/dc
    gao = Tasas_factoring.objects\
        .filter(cxtasa="GAO", empresa = id_empresa.empresa).first()
    if not gao:
        return HttpResponse("no encontró tasa de gao en el sistema."
                +" Registre el cargo con código GAO")

    dc = Tasas_factoring.objects\
        .filter(cxtasa="DCAR", empresa = id_empresa.empresa).first()
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
    cargos = asignacion.ngao + asignacion.ndescuentodecartera
    neto = subtotal - asignacion.niva

    context = {
        "asignacion" : asignacion,
        "documentos" : documentos,
        'gao': dic_gao,
        'dc' : dic_dc,
        'subtotal': subtotal,
        'cargos': cargos,
        'neto': neto,
        'empresa': id_empresa.empresa
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

def ImpresionAntiguedadCartera(request, ):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    facturas = Documentos.objects.antigüedad_por_cliente(id_empresa.empresa)
    accesorios = ChequesAccesorios.objects.antigüedad_por_cliente(id_empresa.empresa)
    prot_facturas = Documentos_protestados.objects.antigüedad_por_cliente_facturas(id_empresa.empresa)
    prot_accesorios = Documentos_protestados.objects.antigüedad_por_cliente_accesorios(id_empresa.empresa)
    acc_quitados = Cheques_quitados.objects.antigüedad_por_cliente(id_empresa.empresa)

    total_facturas = Documentos.objects.antigüedad_cartera(id_empresa.empresa)
    total_accesorios = ChequesAccesorios.objects.antigüedad_cartera(id_empresa.empresa)
    total_protestos = Documentos_protestados.objects.antigüedad_cartera(id_empresa.empresa)
    total_quitados = Cheques_quitados.objects.antigüedad_cartera(id_empresa.empresa)

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

    pvm90 = total_protestos['pvencido_mas_90']
    pv90 = total_protestos['pvencido_90']
    pv60 = total_protestos['pvencido_60']
    pv30 = total_protestos['pvencido_30']
    px30 = total_protestos['pporvencer_30']
    px60 = total_protestos['pporvencer_60']
    px90 = total_protestos['pporvencer_90']
    pxm90 = total_protestos['pporvencer_mas_90']
    if not pvm90: pvm90=0
    if not pv90: pv90 = 0
    if not pv60: pv60 = 0
    if not pv30: pv30 = 0
    if not px30: px30 = 0
    if not px60: px60 = 0
    if not px90: px90 = 0
    if not pxm90: pxm90 = 0

    qvm90 = total_quitados['vencido_mas_90'] 
    qv90 = total_quitados['vencido_90']
    qv60 = total_quitados['vencido_60']
    qv30 = total_quitados['vencido_30']
    qx30 = total_quitados['porvencer_30']
    qx60 = total_quitados['porvencer_60']
    qx90 = total_quitados['porvencer_90']
    qxm90 = total_quitados['porvencer_mas_90']
    if not qvm90: qvm90=0
    if not qv90: qv90=0
    if not qv60: qv60=0
    if not qv30: qv30=0
    if not qx30: qx30=0
    if not qx60: qx60=0
    if not qx90: qx90=0
    if not qxm90: qxm90=0

    template_path = 'operaciones/cartera_reporte.html'

    context = {
        "documentos" : facturas.union(accesorios, prot_facturas, prot_accesorios, acc_quitados),
        "totalvm90"  : fvm90+avm90+pvm90+qvm90,
        "totalv90"   : fv90+av90+pv90+qv90,
        "totalv60"   : fv60+av60+pv60+qv60,
        "totalv30"   : fv30+av30+pv30+qv30,
        "totalx30"   : fx30+ax30+px30+qx30,
        "totalx60"   : fx60+ax60+px60+qx60,
        "totalx90"   : fx90+ax90+px90+qx90,
        "totalxm90"  : fxm90+axm90+pxm90+qxm90,
        "total" : fvm90+fv90+fv60+fv30+avm90+av90+av60+av30+pvm90+pv90+pv60+pv30
                +fxm90+fx90+fx60+fx30+axm90+ax90+ax60+ax30+pxm90+px90+px60+px30
                +qvm90+qv90+qv60+qv30+qx30+qx60+ax90+qxm90,
        'empresa': id_empresa.empresa,
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

from django.db.models import Sum, Q, F, ExpressionWrapper, DateField
from datetime import datetime, timedelta, date

def ImpresionFacturasPendientes(request, clientes = None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    totalfacturas=0
    totalquitados=0
    arr_clientes = []
    
    if clientes != None:
        ids = clientes.split(',')
        for id in ids:
            arr_clientes.append(id)

    template_path = 'operaciones/detalle_facturaspendientes_reporte.html'

    if clientes==None:
        facturas = Documentos.objects.cartera_pendiente(id_empresa.empresa)
        cheques_quitados = ChequesAccesorios.objects.cartera_pendiente(id_empresa.empresa)
    else:
        facturas = Documentos.objects\
                .filter(leliminado = False, nsaldo__gt = 0
                        , cxcliente__in = arr_clientes
                        , cxasignacion__in = Asignacion.objects
                .filter(cxtipo = "F", cxestado = "P"
                        , empresa = id_empresa.empresa
                        , leliminado = False))\
                .values("cxcomprador__cxcomprador__ctnombre"
                        ,"cxcliente__cxcliente__ctnombre"
                        , "cxasignacion__cxasignacion"
                        , "ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "cxasignacion__ddesembolso"
                        , "nsaldo")\
                .annotate(vencimiento = ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                        , output_field=DateField()),
                        dias_vencidos = (date.today() - F('dvencimiento')),
                        dias_negociados = (F('dvencimiento')-F('cxasignacion__ddesembolso')),
                        )\
                .order_by('cxcliente__cxcliente__ctnombre')
          
        cheques_quitados = ChequesAccesorios.objects\
                .filter(laccesorioquitado = True, chequequitado__cxestado = 'A'
                , leliminado = False, lcanjeado = False
                , documento__cxcliente__in = arr_clientes
                , empresa = id_empresa.empresa
                , documento__cxasignacion__cxestado = "P"
                , documento__cxasignacion__leliminado = False)\
                .values("documento__cxcomprador__cxcomprador__ctnombre"
                        , "documento__cxcliente__cxcliente__ctnombre"
                        , "documento__cxasignacion__cxasignacion"
                        , "documento__ctdocumento"
                        , "dvencimiento", "ndiasprorroga"
                        , "documento__cxasignacion__ddesembolso"
                        , "chequequitado__nsaldo")\
                .annotate(vencimiento =ExpressionWrapper( F('dvencimiento') + F('ndiasprorroga')
                                                         , output_field = DateField() ),
                          dias_vencidos = date.today() - F('dvencimiento'),
                          dias_negociados = F('dvencimiento')-F('documento__cxasignacion__ddesembolso'),
                          )\
                .order_by('documento__cxcliente__cxcliente__ctnombre')

    
    totalfacturas = facturas.aggregate(total = Sum('nsaldo'))
    if not totalfacturas['total']: totalfacturas['total']=0

    totalquitados = cheques_quitados.aggregate(total = Sum('chequequitado__nsaldo'))
    if not totalquitados['total']: totalquitados['total']=0
    
    cartera = facturas.union(cheques_quitados).order_by('cxcliente__cxcliente__ctnombre')
    
    context={
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total' : totalfacturas['total'] + totalquitados['total'],
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="facturas_pendientes.pdf"'
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

def ImpresionAccesoriosPendientes(request):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
     
    cartera = ChequesAccesorios.objects.cheques_pendientes(id_empresa.empresa)
    total = cartera.aggregate(total = Sum('ntotal'))

    template_path = 'operaciones/detalle_accesoriospendientes_reporte.html'

    context={
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total': total['total']
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="facturas_pendientes.pdf"'
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

