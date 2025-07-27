import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django_weasyprint import WeasyTemplateResponse
from django.db.models.functions import Cast, ExtractDay
from django.shortcuts import render
from django.db.models import Sum, IntegerField, F, ExpressionWrapper, DateField
from datetime import datetime, timedelta, date
# from xhtml2pdf import pisa

from .models import Asignacion, Documentos, ChequesAccesorios, Cheques_quitados,\
    Pagares, Pagare_detalle, Revision_cartera_detalle, Revision_cartera, \
    Documentos_historico, ChequesAccesorios_historico, Cheques_quitados_historico,\
    Pagare_detalle_historico, Cortes_historico
from cobranzas.models import Documentos_protestados, Documentos_protestados_historico
from empresa.models import Tasas_factoring
from solicitudes import models as SolicitudModels
from bases.models import Usuario_empresa
# from weasyprint import HTML, CSS

FACTURAS_PURAS = 'F'

def ImpresionAsignacionDesdeSolicitud(request, asignacion_id):

        solicitud = SolicitudModels.Asignacion.objects.filter(id= asignacion_id).first()
        
        asgn = Asignacion.objects\
                .filter(id = solicitud.asignacion).first()

        if asgn:
                return ImpresionAsignacion(request, asgn.id)
        else:   
                return HttpResponse("no encontró asignación ")

def ImpresionAsignacion(request, asignacion_id):
    asignacion = Asignacion.objects\
        .filter(id = asignacion_id).first()
    documentos = {}

    id_empresa = Usuario_empresa.objects\
        .filter(user = request.user).first()

    if asignacion.cxtipo==FACTURAS_PURAS:

        template_path = 'operaciones/asignacion_facturas_puras_reporte.html'

        documentos = Documentos.objects\
            .filter(cxasignacion = asignacion)\
                .filter(leliminado = False)\
                .order_by('cxcomprador__cxcomprador__ctnombre')
    else:
        template_path = 'operaciones/asignacion_facturas_accesorios_reporte.html'

        documentos = ChequesAccesorios.objects\
            .filter(leliminado = False
                    , ncanjeadopor = None
                    , documento__in=Documentos.objects\
                        .filter(cxasignacion=asignacion_id))\
                .order_by('documento__cxcomprador__cxcomprador__ctnombre')
                
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
    cargos_negociacion = asignacion.ngao + asignacion.ndescuentodecartera
#     neto = subtotal - asignacion.niva
#  el neto de la asignacion ya incluye los otros cargos
    otros_cargos = asignacion.jotroscargos
    context = {
        "asignacion" : asignacion,
        "documentos" : documentos,
        'gao': dic_gao,
        'dc' : dic_dc,
        'subtotal': subtotal,
        'cargos_negociacion': cargos_negociacion,
        'neto': asignacion.neto(),
        'empresa': id_empresa.empresa,
        'otros_cargos': otros_cargos,
        'fuente': 'operacion'
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="asgn' + str(asignacion_id) + '.pdf"'
    return response

def ImpresionLiquidacion(request, solicitud_id, crear_pdf = False):
    asignacion = SolicitudModels.Asignacion.objects\
        .filter(id = solicitud_id).first()
    documentos = {}

    id_empresa = Usuario_empresa.objects\
        .filter(user = request.user).first()

    if asignacion.cxtipo==FACTURAS_PURAS:

        template_path = 'operaciones/asignacion_facturas_puras_reporte.html'

        documentos = SolicitudModels.Documentos.objects\
            .filter(cxasignacion = asignacion)\
                .filter(leliminado = False)\
                .order_by('comprador__cxcomprador__ctnombre')
    else:
        template_path = 'operaciones/asignacion_facturas_accesorios_reporte.html'

        documentos = SolicitudModels.ChequesAccesorios.objects\
            .filter(leliminado = False
                    # , ncanjeadopor = None
                    , documento__in=SolicitudModels.Documentos.objects\
                        .filter(cxasignacion=asignacion))\
                .order_by('documento__comprador__cxcomprador__ctnombre')
                
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
    cargos_negociacion = asignacion.ngao + asignacion.ndescuentodecartera
#     neto = subtotal - asignacion.niva
#  el neto de la asignacion ya incluye los otros cargos
    otros_cargos = asignacion.jotroscargos

    context = {
        "asignacion" : asignacion,
        "documentos" : documentos,
        'gao': dic_gao,
        'dc' : dic_dc,
        'subtotal': subtotal,
        'cargos_negociacion': cargos_negociacion,
        'neto': asignacion.neto(),
        'empresa': id_empresa.empresa,
        'otros_cargos': otros_cargos,
        'fuente': 'solicitud'
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    if crear_pdf:
        # Guardar el PDF generado en un archivo directamente
        output_filename = os.path.join(settings.MEDIA_ROOT, f"asignacion_{solicitud_id}.pdf")
        with open(output_filename, "wb") as f:
            f.write(response.rendered_content)
        print(f"Archivo PDF creado en: {output_filename}")
        return "OK"
    else:
        # Devolver el PDF para visualización en el navegador
        response['Content-Disposition'] = 'inline; filename="asgn' + str(solicitud_id) + '.pdf"'
        return response

def ImpresionAntiguedadCartera(request):
    id_empresa = Usuario_empresa.objects.filter(user=request.user).first()

    facturas = Documentos.objects.antigüedad_por_cliente(id_empresa.empresa)
    accesorios = ChequesAccesorios.objects.antigüedad_por_cliente(id_empresa.empresa)
    prot_facturas = Documentos_protestados.objects.antigüedad_por_cliente_facturas(id_empresa.empresa)
    prot_accesorios = Documentos_protestados.objects.antigüedad_por_cliente_accesorios(id_empresa.empresa)
    acc_quitados = Cheques_quitados.objects.antigüedad_por_cliente(id_empresa.empresa)
    pagares = Pagare_detalle.objects.antigüedad_por_cliente(id_empresa.empresa)

    total_facturas = Documentos.objects.antigüedad_cartera(id_empresa.empresa)
    total_accesorios = ChequesAccesorios.objects.antigüedad_cartera(id_empresa.empresa)
    total_protestos = Documentos_protestados.objects.antigüedad_cartera(id_empresa.empresa)
    total_quitados = Cheques_quitados.objects.antigüedad_cartera(id_empresa.empresa)
    total_pagares = Pagare_detalle.objects.antigüedad_cartera(id_empresa.empresa)

    fvm90 = total_facturas['vencido_mas_90'] or 0
    fv90 = total_facturas['vencido_90'] or 0
    fv60 = total_facturas['vencido_60'] or 0
    fv30 = total_facturas['vencido_30'] or 0
    fx30 = total_facturas['porvencer_30'] or 0
    fx60 = total_facturas['porvencer_60'] or 0
    fx90 = total_facturas['porvencer_90'] or 0
    fxm90 = total_facturas['porvencer_mas_90'] or 0

    avm90 = total_accesorios['vencido_mas_90'] or 0
    av90 = total_accesorios['vencido_90'] or 0
    av60 = total_accesorios['vencido_60'] or 0
    av30 = total_accesorios['vencido_30'] or 0
    ax30 = total_accesorios['porvencer_30'] or 0
    ax60 = total_accesorios['porvencer_60'] or 0
    ax90 = total_accesorios['porvencer_90'] or 0
    axm90 = total_accesorios['porvencer_mas_90'] or 0

    pvm90 = total_protestos['pvencido_mas_90'] or 0
    pv90 = total_protestos['pvencido_90'] or 0
    pv60 = total_protestos['pvencido_60'] or 0
    pv30 = total_protestos['pvencido_30'] or 0
    px30 = total_protestos['pporvencer_30'] or 0
    px60 = total_protestos['pporvencer_60'] or 0
    px90 = total_protestos['pporvencer_90'] or 0
    pxm90 = total_protestos['pporvencer_mas_90'] or 0

    qvm90 = total_quitados['vencido_mas_90'] or 0
    qv90 = total_quitados['vencido_90'] or 0
    qv60 = total_quitados['vencido_60'] or 0
    qv30 = total_quitados['vencido_30'] or 0
    qx30 = total_quitados['porvencer_30'] or 0
    qx60 = total_quitados['porvencer_60'] or 0
    qx90 = total_quitados['porvencer_90'] or 0
    qxm90 = total_quitados['porvencer_mas_90'] or 0

    cvm90 = total_pagares['vencido_mas_90'] or 0
    cv90 = total_pagares['vencido_90'] or 0
    cv60 = total_pagares['vencido_60'] or 0
    cv30 = total_pagares['vencido_30'] or 0
    cx30 = total_pagares['porvencer_30'] or 0
    cx60 = total_pagares['porvencer_60'] or 0
    cx90 = total_pagares['porvencer_90'] or 0
    cxm90 = total_pagares['porvencer_mas_90'] or 0

    template_path = 'operaciones/cartera_reporte.html'
    detalle = facturas.union(accesorios, prot_facturas, prot_accesorios, acc_quitados, pagares)\
            .order_by('cxcliente__cxcliente__ctnombre')

    # Acumular totales por cliente
    acumulado_por_cliente = {}
    for doc in detalle:
        cliente = doc['cxcliente__cxcliente__ctnombre']
        if cliente not in acumulado_por_cliente:
            acumulado_por_cliente[cliente] = {
                'vencido_mas_90': 0,
                'vencido_90': 0,
                'vencido_60': 0,
                'vencido_30': 0,
                'porvencer_30': 0,
                'porvencer_60': 0,
                'porvencer_90': 0,
                'porvencer_mas_90': 0,
                'total': 0
            }
        acumulado_por_cliente[cliente]['vencido_mas_90'] += doc.get('vencido_mas_90', 0) or 0
        acumulado_por_cliente[cliente]['vencido_90'] += doc.get('vencido_90', 0) or 0
        acumulado_por_cliente[cliente]['vencido_60'] += doc.get('vencido_60', 0) or 0
        acumulado_por_cliente[cliente]['vencido_30'] += doc.get('vencido_30', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_30'] += doc.get('porvencer_30', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_60'] += doc.get('porvencer_60', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_90'] += doc.get('porvencer_90', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_mas_90'] += doc.get('porvencer_mas_90', 0) or 0
        acumulado_por_cliente[cliente]['total'] += doc.get('total', 0) or 0

    context = {
        "documentos": acumulado_por_cliente,
        "totalvm90": fvm90 + avm90 + pvm90 + qvm90 + cvm90,
        "totalv90": fv90 + av90 + pv90 + qv90 + cv90,
        "totalv60": fv60 + av60 + pv60 + qv60 + cv60,
        "totalv30": fv30 + av30 + pv30 + qv30 + cv30,
        "totalx30": fx30 + ax30 + px30 + qx30 + cx30,
        "totalx60": fx60 + ax60 + px60 + qx60 + cx60,
        "totalx90": fx90 + ax90 + px90 + qx90 + cx90,
        "totalxm90": fxm90 + axm90 + pxm90 + qxm90 + cxm90,
        "total": fvm90 + fv90 + fv60 + fv30 + avm90 + av90 + av60 + av30 + pvm90 + pv90 + pv60 + pv30
                + fxm90 + fx90 + fx60 + fx30 + axm90 + ax90 + ax60 + ax30 + pxm90 + px90 + px60 + px30
                + qvm90 + qv90 + qv60 + qv30 + qx30 + qx60 + ax90 + qxm90
                + cvm90 + cv90 + cv60 + cv30 + cx30 + cx60 + cx90 + cxm90,
        'empresa': id_empresa.empresa,
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="cartera.pdf"'
    return response

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
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
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
                        dias_vencidos=Cast(ExtractDay(ExpressionWrapper(date.today() - F('dvencimiento')
                                                                            , output_field=DateField()))
                                                , IntegerField()),
                        dias_negociados=Cast(ExtractDay(ExpressionWrapper(F('dvencimiento')
                                                                          -F('documento__cxasignacion__ddesembolso')
                                                                          , output_field=DateField()))
                                                , IntegerField()),
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
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="factueas pendientes.pdf"'
    return response

def ImpresionAccesoriosPendientes(request, id_cliente=None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
#     se esta filtrando por un solo cliente por lo que el arreglo no hace falta
#     arr_clientes = []
     
#     if clientes != None:
#         ids = clientes.split(',')
#         for id in ids:
#             arr_clientes.append(id)

    if id_cliente == None:
        cartera = ChequesAccesorios.objects.cheques_pendientes(id_empresa.empresa)
    else:
        cartera = ChequesAccesorios.objects.cheques_pendientes_cliente(id_cliente)

    total = cartera.aggregate(total = Sum('ntotal'))

    template_path = 'operaciones/detalle_accesoriospendientes_reporte.html'

    context={
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total': total['total']
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="facturas_pendientes.pdf"'
    return response

def ImpresionResumenAsignaciones(request, desde, hasta, clientes=None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
     
    arr_clientes = []
    
    if clientes != None:
        ids = clientes.split(',')
        for id in ids:
            arr_clientes.append(id)

    template_path = 'operaciones/resumen_asignaciones_reporte.html'

    if clientes == None:
        cartera = Asignacion.objects\
            .filter(ddesembolso__gte = desde,
                    ddesembolso__lte = hasta,
                    empresa = id_empresa.empresa,
                    leliminado = False)\
            .order_by('cxtipofactoring', 'ddesembolso')
    else:
        cartera = Asignacion.objects\
            .filter(ddesembolso__gte = desde,
                    ddesembolso__lte = hasta,
                    cxcliente__in = arr_clientes,
                    empresa = id_empresa.empresa,
                    leliminado = False)\
            .order_by('cxtipofactoring', 'ddesembolso')

    total = cartera.aggregate(
        total = Sum('nvalor'),
        cargos = Sum('ngao') + Sum('ndescuentodecartera') + Sum('notroscargos'),
        neto = Sum('nanticipo') - Sum('ngao') - Sum('ndescuentodecartera') 
            - Sum('notroscargos'),
        iva = Sum('niva'),
        )

    context={
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total_negociado': total['total'],
        'total_cargos': total['cargos'],
        'total_neto': total['neto'],
        'total_iva': total['iva'],
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="resumen_asignaciones.pdf"'
    return response

def ImpresionPagare(request, pagare_id):
    pagare = Pagares.objects.filter(id = pagare_id).first()
    cuotas = {}

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    template_path = 'operaciones/pagare_reporte.html'

    cuotas = Pagare_detalle.objects\
        .filter(leliminado = False, pagare = pagare)\
        .order_by('ncuota')
                
    
    context = {
        "pagare" : pagare,
        "cuotas" : cuotas,
        'total': pagare.valor_total(),
        'empresa': id_empresa.empresa,
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="pagare "' + str(pagare_id) + ".pdf"
    return response

def ImpresionPagaresPendientes(request, clientes=None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    total = 0
    template_path = 'operaciones/detalle_pagarespendientes_reporte.html'
    arr_clientes = []
    
    if clientes != None:
        ids = clientes.split(',')
        for id in ids:
            arr_clientes.append(id)

    if clientes == None:
        cartera = Pagare_detalle.objects\
            .filter(empresa = id_empresa.empresa
                    , leliminado = False, nsaldo__gt = 0)\
            .order_by('pagare_cxcliente__cxcliente__ctnombre', 'dfechapago')
    else:
        cartera = Pagare_detalle.objects\
            .filter(empresa = id_empresa.empresa
                    , leliminado = False, nsaldo__gt = 0
                    , pagare__cxcliente__in = arr_clientes)\
            .order_by('pagare__cxcliente__cxcliente__ctnombre', 'dfechapago')

    total = cartera.aggregate(total = Sum('nsaldo'))
    
    context={
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total': total['total']
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="pagares_pendientes.pdf"'
    return response

def ImpresionRevisionCartera(request, revision_id, ):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
     
    template_path = 'operaciones/revisioncartera_reporte.html'

    revision = Revision_cartera.objects.filter(id = revision_id).first()

    detalle = Revision_cartera_detalle.objects\
        .filter(revision = revision_id,
                empresa = id_empresa.empresa,
                leliminado = False)\
        .order_by('cxcliente__cxcliente__ctnombre')

    total = detalle.aggregate(
        vencido_mas_60 = Sum('nvencidomas60'),
        vencido_60 = Sum('nvencido60'),
        vencido_30 = Sum('nvencido30'),
        por_vencer = Sum('nporvencer') ,
        protesto = Sum('nprotesto'),
        )

    context={
        "detalle" : detalle,
        "revision" : revision,
        'empresa': id_empresa.empresa,
        'total_vencido_mas_60': total['vencido_mas_60'],
        'total_vencido_60': total['vencido_60'],
        'total_vencido_30': total['vencido_30'],
        'total_por_vencer': total['por_vencer'],
        'total_protesto': total['protesto'],
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="resumen_asignaciones.pdf"'
    return response

def ImpresionAntiguedadCarteraCorte(request, corte_id):
    id_empresa = Usuario_empresa.objects.filter(user=request.user).first()

    corte = Cortes_historico.objects.filter(id=corte_id).first()

    facturas = Documentos_historico.objects.antigüedad_por_cliente(id_empresa.empresa, corte_id)
    accesorios = ChequesAccesorios_historico.objects.antigüedad_por_cliente(id_empresa.empresa, corte_id)
    prot_facturas = Documentos_protestados_historico.objects.antigüedad_por_cliente_facturas(id_empresa.empresa, corte_id)
    prot_accesorios = Documentos_protestados_historico.objects.antigüedad_por_cliente_accesorios(id_empresa.empresa, corte_id)
    acc_quitados = Cheques_quitados_historico.objects.antigüedad_por_cliente(id_empresa.empresa, corte_id)
    pagares = Pagare_detalle_historico.objects.antigüedad_por_cliente(id_empresa.empresa, corte_id)

    total_facturas = Documentos_historico.objects.antigüedad_cartera(id_empresa.empresa, corte_id)
    total_accesorios = ChequesAccesorios_historico.objects.antigüedad_cartera(id_empresa.empresa, corte_id)
    total_protestos = Documentos_protestados_historico.objects.antigüedad_cartera(id_empresa.empresa, corte_id)
    total_quitados = Cheques_quitados_historico.objects.antigüedad_cartera(id_empresa.empresa, corte_id)
    total_pagares = Pagare_detalle_historico.objects.antigüedad_cartera(id_empresa.empresa, corte_id)

    fvm90 = total_facturas['vencido_mas_90'] or 0
    fv90 = total_facturas['vencido_90'] or 0
    fv60 = total_facturas['vencido_60'] or 0
    fv30 = total_facturas['vencido_30'] or 0
    fx30 = total_facturas['porvencer_30'] or 0
    fx60 = total_facturas['porvencer_60'] or 0
    fx90 = total_facturas['porvencer_90'] or 0
    fxm90 = total_facturas['porvencer_mas_90'] or 0

    avm90 = total_accesorios['vencido_mas_90'] or 0
    av90 = total_accesorios['vencido_90'] or 0
    av60 = total_accesorios['vencido_60'] or 0
    av30 = total_accesorios['vencido_30'] or 0
    ax30 = total_accesorios['porvencer_30'] or 0
    ax60 = total_accesorios['porvencer_60'] or 0
    ax90 = total_accesorios['porvencer_90'] or 0
    axm90 = total_accesorios['porvencer_mas_90'] or 0

    pvm90 = total_protestos['pvencido_mas_90'] or 0
    pv90 = total_protestos['pvencido_90'] or 0
    pv60 = total_protestos['pvencido_60'] or 0
    pv30 = total_protestos['pvencido_30'] or 0
    px30 = total_protestos['pporvencer_30'] or 0
    px60 = total_protestos['pporvencer_60'] or 0
    px90 = total_protestos['pporvencer_90'] or 0
    pxm90 = total_protestos['pporvencer_mas_90'] or 0

    qvm90 = total_quitados['vencido_mas_90'] or 0
    qv90 = total_quitados['vencido_90'] or 0
    qv60 = total_quitados['vencido_60'] or 0
    qv30 = total_quitados['vencido_30'] or 0
    qx30 = total_quitados['porvencer_30'] or 0
    qx60 = total_quitados['porvencer_60'] or 0
    qx90 = total_quitados['porvencer_90'] or 0
    qxm90 = total_quitados['porvencer_mas_90'] or 0

    cvm90 = total_pagares['vencido_mas_90'] or 0
    cv90 = total_pagares['vencido_90'] or 0
    cv60 = total_pagares['vencido_60'] or 0
    cv30 = total_pagares['vencido_30'] or 0
    cx30 = total_pagares['porvencer_30'] or 0
    cx60 = total_pagares['porvencer_60'] or 0
    cx90 = total_pagares['porvencer_90'] or 0
    cxm90 = total_pagares['porvencer_mas_90'] or 0

    template_path = 'operaciones/cartera_reporte.html'
    detalle = facturas.union(accesorios, prot_facturas, prot_accesorios, acc_quitados, pagares)\
            .order_by('cxcliente__cxcliente__ctnombre')

    # Acumular totales por cliente
    acumulado_por_cliente = {}
    for doc in detalle:
        cliente = doc['cxcliente__cxcliente__ctnombre']
        if cliente not in acumulado_por_cliente:
            acumulado_por_cliente[cliente] = {
                'vencido_mas_90': 0,
                'vencido_90': 0,
                'vencido_60': 0,
                'vencido_30': 0,
                'porvencer_30': 0,
                'porvencer_60': 0,
                'porvencer_90': 0,
                'porvencer_mas_90': 0,
                'total': 0
            }
        acumulado_por_cliente[cliente]['vencido_mas_90'] += doc.get('vencido_mas_90', 0) or 0
        acumulado_por_cliente[cliente]['vencido_90'] += doc.get('vencido_90', 0) or 0
        acumulado_por_cliente[cliente]['vencido_60'] += doc.get('vencido_60', 0) or 0
        acumulado_por_cliente[cliente]['vencido_30'] += doc.get('vencido_30', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_30'] += doc.get('porvencer_30', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_60'] += doc.get('porvencer_60', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_90'] += doc.get('porvencer_90', 0) or 0
        acumulado_por_cliente[cliente]['porvencer_mas_90'] += doc.get('porvencer_mas_90', 0) or 0
        acumulado_por_cliente[cliente]['total'] += doc.get('total', 0) or 0

    context = {
        "corte" : corte,
        "documentos": acumulado_por_cliente,
        "totalvm90": fvm90 + avm90 + pvm90 + qvm90 + cvm90,
        "totalv90": fv90 + av90 + pv90 + qv90 + cv90,
        "totalv60": fv60 + av60 + pv60 + qv60 + cv60,
        "totalv30": fv30 + av30 + pv30 + qv30 + cv30,
        "totalx30": fx30 + ax30 + px30 + qx30 + cx30,
        "totalx60": fx60 + ax60 + px60 + qx60 + cx60,
        "totalx90": fx90 + ax90 + px90 + qx90 + cx90,
        "totalxm90": fxm90 + axm90 + pxm90 + qxm90 + cxm90,
        "total": fvm90 + fv90 + fv60 + fv30 + avm90 + av90 + av60 + av30 + pvm90 + pv90 + pv60 + pv30
                + fxm90 + fx90 + fx60 + fx30 + axm90 + ax90 + ax60 + ax30 + pxm90 + px90 + px60 + px30
                + qvm90 + qv90 + qv60 + qv30 + qx30 + qx60 + ax90 + qxm90
                + cvm90 + cv90 + cv60 + cv30 + cx30 + cx60 + cx90 + cxm90,
        'empresa': id_empresa.empresa,
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="cartera historica.pdf"'
    return response

def ImpresionFacturasPendientesCorte(request, corte_id):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    corte = Cortes_historico.objects.filter(id=corte_id).first()
    totalfacturas=0
    totalquitados=0

    template_path = 'operaciones/detalle_facturaspendientes_reporte.html'

    facturas = Documentos_historico.objects\
        .cartera_pendiente(id_empresa.empresa, corte_id)
    cheques_quitados = ChequesAccesorios_historico\
        .objects.cartera_pendiente(id_empresa.empresa, corte_id)
    
    totalfacturas = facturas.aggregate(total = Sum('nsaldo'))
    if not totalfacturas['total']: totalfacturas['total']=0

    totalquitados = cheques_quitados.aggregate(total = Sum('chequequitado__nsaldo'))
    if not totalquitados['total']: totalquitados['total']=0
    
    cartera = facturas.union(cheques_quitados).order_by('cxcliente__cxcliente__ctnombre')
    
    context={
        "corte" : corte,
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total' : totalfacturas['total'] + totalquitados['total'],
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="factueas pendientes.pdf"'
    return response

def ImpresionAccesoriosPendientesCorte(request, corte_id=None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    corte = Cortes_historico.objects.filter(id=corte_id).first()

    cartera = ChequesAccesorios_historico.objects\
        .cheques_pendientes(id_empresa.empresa, corte_id)

    total = cartera.aggregate(total = Sum('ntotal'))

    template_path = 'operaciones/detalle_accesoriospendientes_reporte.html'

    context={
        "corte" : corte,
        "detalle" : cartera,
        'empresa': id_empresa.empresa,
        'total': total['total']
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="facturas_pendientes.pdf"'
    return response

def ImpresionAntiguedadCarteraPorDeudor(request, id_cliente, cliente):
    id_empresa = Usuario_empresa.objects.filter(user=request.user).first()

    facturas = Documentos.objects\
        .antigüedad_por_deudor(id_empresa.empresa, id_cliente)
    accesorios = ChequesAccesorios.objects\
        .antigüedad_por_deudor(id_empresa.empresa, id_cliente)
    prot_facturas = Documentos_protestados.objects\
        .antigüedad_por_deudor_facturas(id_empresa.empresa, id_cliente)
    prot_accesorios = Documentos_protestados.objects\
        .antigüedad_por_deudor_accesorios(id_empresa.empresa, id_cliente)
    acc_quitados = Cheques_quitados.objects\
        .antigüedad_por_deudor(id_empresa.empresa, id_cliente)

    total_facturas = Documentos.objects\
        .antigüedad_cartera(id_empresa.empresa, id_cliente)
    total_accesorios = ChequesAccesorios.objects\
        .antigüedad_cartera(id_empresa.empresa, id_cliente)
    total_protestos = Documentos_protestados.objects\
        .antigüedad_cartera(id_empresa.empresa, id_cliente)
    total_quitados = Cheques_quitados.objects\
        .antigüedad_cartera(id_empresa.empresa, id_cliente)

    fvm90 = total_facturas['vencido_mas_90'] or 0
    fv90 = total_facturas['vencido_90'] or 0
    fv60 = total_facturas['vencido_60'] or 0
    fv30 = total_facturas['vencido_30'] or 0
    fx30 = total_facturas['porvencer_30'] or 0
    fx60 = total_facturas['porvencer_60'] or 0
    fx90 = total_facturas['porvencer_90'] or 0
    fxm90 = total_facturas['porvencer_mas_90'] or 0

    avm90 = total_accesorios['vencido_mas_90'] or 0
    av90 = total_accesorios['vencido_90'] or 0
    av60 = total_accesorios['vencido_60'] or 0
    av30 = total_accesorios['vencido_30'] or 0
    ax30 = total_accesorios['porvencer_30'] or 0
    ax60 = total_accesorios['porvencer_60'] or 0
    ax90 = total_accesorios['porvencer_90'] or 0
    axm90 = total_accesorios['porvencer_mas_90'] or 0

    pvm90 = total_protestos['pvencido_mas_90'] or 0
    pv90 = total_protestos['pvencido_90'] or 0
    pv60 = total_protestos['pvencido_60'] or 0
    pv30 = total_protestos['pvencido_30'] or 0
    px30 = total_protestos['pporvencer_30'] or 0
    px60 = total_protestos['pporvencer_60'] or 0
    px90 = total_protestos['pporvencer_90'] or 0
    pxm90 = total_protestos['pporvencer_mas_90'] or 0

    qvm90 = total_quitados['vencido_mas_90'] or 0
    qv90 = total_quitados['vencido_90'] or 0
    qv60 = total_quitados['vencido_60'] or 0
    qv30 = total_quitados['vencido_30'] or 0
    qx30 = total_quitados['porvencer_30'] or 0
    qx60 = total_quitados['porvencer_60'] or 0
    qx90 = total_quitados['porvencer_90'] or 0
    qxm90 = total_quitados['porvencer_mas_90'] or 0

    template_path = 'operaciones/carteradeudor_reporte.html'
    detalle = facturas.union(accesorios, prot_facturas
                             , prot_accesorios, acc_quitados, )\
            .order_by('cxcomprador__cxcomprador__ctnombre')
    print('detalle', detalle)
    # Acumular totales por deudor
    acumulado_por_deudor = {}
    for doc in detalle:
        deudor = doc['cxcomprador__cxcomprador__ctnombre']
        print('deudor', deudor)
        if deudor not in acumulado_por_deudor:
            acumulado_por_deudor[deudor] = {
                'vencido_mas_90': 0,
                'vencido_90': 0,
                'vencido_60': 0,
                'vencido_30': 0,
                'porvencer_30': 0,
                'porvencer_60': 0,
                'porvencer_90': 0,
                'porvencer_mas_90': 0,
                'total': 0
            }
        acumulado_por_deudor[deudor]['vencido_mas_90'] += doc.get('vencido_mas_90', 0) or 0
        acumulado_por_deudor[deudor]['vencido_90'] += doc.get('vencido_90', 0) or 0
        acumulado_por_deudor[deudor]['vencido_60'] += doc.get('vencido_60', 0) or 0
        acumulado_por_deudor[deudor]['vencido_30'] += doc.get('vencido_30', 0) or 0
        acumulado_por_deudor[deudor]['porvencer_30'] += doc.get('porvencer_30', 0) or 0
        acumulado_por_deudor[deudor]['porvencer_60'] += doc.get('porvencer_60', 0) or 0
        acumulado_por_deudor[deudor]['porvencer_90'] += doc.get('porvencer_90', 0) or 0
        acumulado_por_deudor[deudor]['porvencer_mas_90'] += doc.get('porvencer_mas_90', 0) or 0
        acumulado_por_deudor[deudor]['total'] += doc.get('total', 0) or 0

    context = {
        "documentos": acumulado_por_deudor,
        "totalvm90": fvm90 + avm90 + pvm90 + qvm90,
        "totalv90": fv90 + av90 + pv90 + qv90,
        "totalv60": fv60 + av60 + pv60 + qv60,
        "totalv30": fv30 + av30 + pv30 + qv30,
        "totalx30": fx30 + ax30 + px30 + qx30,
        "totalx60": fx60 + ax60 + px60 + qx60,
        "totalx90": fx90 + ax90 + px90 + qx90,
        "totalxm90": fxm90 + axm90 + pxm90 + qxm90,
        "total": fvm90 + fv90 + fv60 + fv30 + avm90 + av90 + av60 + av30 + pvm90 + pv90 + pv60 + pv30
                + fxm90 + fx90 + fx60 + fx30 + axm90 + ax90 + ax60 + ax30 + pxm90 + px90 + px60 + px30
                + qvm90 + qv90 + qv60 + qv30 + qx30 + qx60 + ax90 + qxm90,
        'empresa': id_empresa.empresa,
        'cliente': cliente
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="cartera_por_deudor.pdf"'
    return response

