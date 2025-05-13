import os
import json
import calendar
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django_weasyprint import WeasyTemplateResponse

from .models import  Diario_cabecera, Transaccion, Plan_cuentas, Control_meses

from bases.models import Usuario_empresa

# # from xhtml2pdf import pisa
# from weasyprint import HTML, CSS

from bases.views import enviarPost, enviarConsulta


def ImpresionDiarioContable(request, diario_id):
    detalle = {}
    template_path = 'contabilidad/diario_contable_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # tomar el codigo de asignacion grabado en la solicitud
    diario = Diario_cabecera.objects.filter(id= diario_id).first()
    
    if not diario:
        return HttpResponse("no encontró diario contable "+ str(diario_id))

    # cuando la forma de pago es DEP es deposito de accesorios y de ahí debe
    # tomar la fecha de vencimiento
    detalle = Transaccion.objects.filter(diario = diario_id, leliminado = False)

    # totales
    tot_cobro_d = detalle.filter(cxtipo='D').aggregate(tot_debe=Sum('nvalor'))
    tot_cobro_h = detalle.filter(cxtipo='H').aggregate(tot_haber=Sum('nvalor'))

    totales = {
        "debe":tot_cobro_d["tot_debe"],
        "haber":tot_cobro_h["tot_haber"]
    }


    context = {
        "diario" : diario,
        "detalle" : detalle,
        "totales": totales,
        'empresa': id_empresa.empresa
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="diario "' \
        + str(diario.cxtransaccion) + ".pdf"
    return response

def ImpresionComprobanteEgreso(request, diario_id):
    detalle = {}
    template_path = 'contabilidad/comprobante_egreso_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # tomar el codigo de asignacion grabado en la solicitud
    diario = Diario_cabecera.objects.filter(id= diario_id).first()
    
    if not diario:
        return HttpResponse("no encontró diario contable")

    
    # cuando la forma de pago es DEP es deposito de accesorios y de ahí debe
    # tomar la fecha de vencimiento
    detalle = Transaccion.objects\
        .filter(diario = diario_id, leliminado = False)

    # totales
    tot_cobro_d = detalle.filter(cxtipo='D').aggregate(tot_debe=Sum('nvalor'))
    tot_cobro_h = detalle.filter(cxtipo='H').aggregate(tot_haber=Sum('nvalor'))

    totales = {
        "debe":tot_cobro_d["tot_debe"],
        "haber":tot_cobro_h["tot_haber"]
    }


    context = {
        "diario" : diario,
        "detalle" : detalle,
        "totales": totales,
        'empresa': id_empresa.empresa
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="egreso "' \
        + str(diario.cxtransaccion) + ".pdf"
    return response

def ImpresionPlanDeCuentas(request):
    template_path = 'contabilidad/plandecuentas_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    detalle = Plan_cuentas.objects.filter(empresa = id_empresa.empresa)\
        .order_by('cxcuenta')

    context = {
        "detalle" : detalle,
        'empresa': id_empresa.empresa
    }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="plan de cuentas.pdf"'
    return response    
      
def ImpresionBalanceGeneral(request, año, mes):
    template_path = 'contabilidad/balance_general_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    cerrado = Control_meses.objects.filter(empresa = id_empresa.empresa
                                           , año = año, mes=mes).first()
    if not cerrado or not cerrado.lbloqueado:
        data = enviarConsulta("SELECT * FROM uspGeneraBGAcumulado('{0}',{1},{2})"
                            .format(año, mes,  id_empresa.empresa.id))
    else:
        data = enviarConsulta("SELECT * FROM uspImprimeBGAcumulado('{0}',{1},{2})"
                            .format(año, mes,  id_empresa.empresa.id))
    if not data:
        return HttpResponse ("Ningún dato encontrado para "+año + "-" + mes)

    result = []
    for r in data:
        result.append( r[0])
    
    last_day = calendar.monthrange(int(año), int(mes))[1]
    # convertir string a date?
    fecha = datetime.strptime(año+"-"+mes+"-"+str(last_day), "%Y-%m-%d")

    # total pasivo y patrimonio
    pyp = result[0]['totalpasivopatrimonio']
    
    context = {
         'activo': result,
         'empresa': id_empresa.empresa,
         'fecha_corte':fecha,
         'pasivo_patrimonio':pyp,
      }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="balance general '\
          +año+'-'+str(mes)+ '.pdf"'
    return response    
      
def ImpresionPerdidasyGanancias(request, año, mes,):
    template_path = 'contabilidad/perdidasyganancias_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    cerrado = Control_meses.objects.filter(empresa = id_empresa.empresa
                                           , año = año, mes=mes).first()
    if not cerrado or not cerrado.lbloqueado:
        data = enviarConsulta("SELECT * FROM uspGeneraPyGAcumulado('{0}',{1},{2})"
                            .format(año, mes,  id_empresa.empresa.id))
    else:
        data = enviarConsulta("SELECT * FROM uspImprimePyGAcumulado('{0}',{1},{2})"
                            .format(año, mes,  id_empresa.empresa.id))
    if not data:
        return HttpResponse ("Ningún dato encontrado para "+año + "-" + mes)
    
    result = []
    for r in data:
        result.append( r[0])
    
    last_day = calendar.monthrange(int(año), int(mes))[1]
    # convertir string a date?
    fecha = datetime.strptime(año+"-"+mes+"-"+str(last_day), "%Y-%m-%d")
    
    context = {
         'activo': result,
         'empresa': id_empresa.empresa,
         'fecha_corte':fecha
      }

    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="estado p&g  '\
          +año+'-'+str(mes)+ '.pdf"'
    return response      