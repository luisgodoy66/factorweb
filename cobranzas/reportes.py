import os
import json

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.staticfiles import finders

from .models import  Documentos_cabecera, Documentos_detalle, Liquidacion_cabecera\
        , Liquidacion_detalle, Recuperaciones_cabecera, Recuperaciones_detalle\
        , Cheques, Cheques_protestados, Cargos_cabecera, Cargos_detalle

from operaciones.models import Notas_debito_cabecera

from empresa.models import Tasas_factoring

from xhtml2pdf import pisa

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

def ImpresionCobranzaCartera(request, cobranza_id):
    detalle = {}
    template_path = 'cobranzas/cobranzas_cartera_reporte.html'
    forma_cobro = ''
    datos_deposito='N/A'
    codigo_forma = ''
    fecha_protesto=''
    motivo_protesto=''
    nd_protesto = 0
    # tomar el codigo de asignacion grabado en la solicitud
    cobranza = Documentos_cabecera.objects.filter(id= cobranza_id).first()
    
    if not cobranza:
        return HttpResponse("no encontró cobranza ")

    # cuando la forma de pago es DEP es deposito de accesorios y de ahí debe
    # tomar la fecha de vencimiento
    detalle = Documentos_detalle.objects\
        .filter(cxcobranza = cobranza_id, leliminado = False)

    codigo_forma = cobranza.cxformapago

    # cargar forma de cobro
    if cobranza.cxformapago=="MOV":
        forma_cobro = 'Movimiento contable'
    else:
        if cobranza.lpagadoporelcliente:
                forma_cobro = 'Cliente '
        else:
                forma_cobro = 'Deudor '

    if cobranza.cxformapago=="EFE":
        forma_cobro += "paga en efectivo"
    if cobranza.cxformapago=="TRA":
        forma_cobro += 'transfiere de ' + cobranza.cxcuentatransferencia.__str__()
    if cobranza.cxformapago=="CHE":
        forma_cobro += 'emite cheque ' + cobranza.cxcheque.__str__()
    if cobranza.cxformapago=="DEP":
        forma_cobro = 'Se depositó accesorio ' + cobranza.cxcheque.__str__()
    
    if cobranza.cxformapago != "MOV":
        datos_deposito = cobranza.ddeposito.strftime("%Y/%m/%d")

        if cobranza.ldepositoencuentaconjunta:
                datos_deposito += ' en cuenta del cliente'
        else:
                datos_deposito += ' en ' + cobranza.cxcuentadeposito.__str__()

    # totales
    tot_cobro = detalle.aggregate(Sum('nvalorcobranza'))
    tot_retenciones = detalle.aggregate(Sum('nretenciones'))
    tot_bajas = detalle.aggregate(Sum('nvalorbaja'))

    totales = {
        "cobrado":tot_cobro["nvalorcobranza__sum"]
        , "retenido": tot_retenciones["nretenciones__sum"]
        , "bajas":tot_bajas["nvalorbaja__sum"]
        , "aplicado":tot_cobro["nvalorcobranza__sum"]
                +tot_retenciones["nretenciones__sum"]
                +tot_bajas["nvalorbaja__sum"]
    }

    # si cobranza esta protstada, enviar datos del protestp
    if cobranza.cxestado=='P':
        cheque = Cheques.objects.filter(pk = cobranza.cxcheque.id).first()
        protesto = Cheques_protestados.objects.filter(cheque = cheque).first()
        if protesto:
            fecha_protesto = protesto.dprotesto
            motivo_protesto = protesto.motivoprotesto.ctmotivoprotesto
            if protesto.notadedebito:
                nd_protesto = protesto.notadedebito.nvalor
            else:
                nd_protesto = None

    context = {
        "cobranza" : cobranza,
        "detalle" : detalle,
        "datos_forma_cobro" : forma_cobro,
        "datos_deposito" : datos_deposito,
        "forma_cobro": codigo_forma,
        "totales": totales,
        "fecha_protesto": fecha_protesto,
        "motivo_protesto": motivo_protesto,
        "nd_protesto":nd_protesto,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="cobranza "' + str(cobranza.cxcobranza) + ".pdf"
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

def ImpresionLiquidacion(request, liquidacion_id):
    template_name = 'cobranzas/liquidacion_reporte.html'

    liquidacion = Liquidacion_cabecera.objects.filter(pk = liquidacion_id).first()

    detalle_cargos = Liquidacion_detalle.objects.filter(liquidacion = liquidacion)\
        .order_by('-cargo__cxmovimiento__nprioridad', 'cargo__cxmovimiento')

    # datos de tasa gao/dc
    gao = Tasas_factoring.objects.filter(cxtasa="GAO").first()
    if not gao:
        return HttpResponse("no encontró tasa de gao")

    dc = Tasas_factoring.objects.filter(cxtasa="DCAR").first()
    if not dc:
        return HttpResponse("no encontró tasa de descuento de catera")

    gaoa = Tasas_factoring.objects.filter(cxtasa="GAOA").first()

    # crear un objeto json agrupando los cargos por código y que haya un elemento
    # json que contenga el detalle de cada cobranza.
    idcargo=""
    totalcargo = 0
    listadetalle = []
    listacargos=[]

    for i in range(len(detalle_cargos)):
        item = detalle_cargos[i]

        if idcargo != item.cargo.cxmovimiento.ctmovimiento and idcargo !="":
            
            jscab={}
            jscab["nombre"] = idcargo
            jscab["valor"] = totalcargo
            jscab["detalle"] = listadetalle

            listacargos.append(jscab)

            totalcargo=0
            jsdet={}
            listadetalle = []

        idcargo = item.cargo.cxmovimiento.ctmovimiento

        jsdet={}
        if item.cargo.cxasignacion != None:
            jsdet["asignacion"] = item.cargo.cxasignacion
        # el IVA no tiene documento, porque es general a la Liquidacion
        if item.cargo.cxasignacion:
            jsdet["documento"] = item.cargo.cxdocumento.ctdocumento
            jsdet["desembolso"] = item.cargo.cxasignacion.ddesembolso
        
        # se guarda el código de la operación y no el pk
        # la operacion puede ser cobranza o recuperacion
        if item.cxtipooperacion=="C":
            operacion = Documentos_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='R':
            operacion = Recuperaciones_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='D':
            operacion = Notas_debito_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='L':
            operacion = Liquidacion_cabecera.objects.filter(pk=item.operacion).first()

        jsdet["cobranza"] = operacion
        # cuando el tipo es D (nota de debito), se puede buscar si es de cuenta conjunta
        # y tomar el motivo para mostrarlo en el reporte
        jsdet["valor_base"] = item.cargo.ctvalorbase
        jsdet["tasa_calculo"]=item.cargo.ntasacalculo
        jsdet["dias_calculo"] = item.cargo.ndiascalculo
        jsdet["valor"] = item.cargo.nvalor

        listadetalle.append(jsdet)

        totalcargo += item.cargo.nvalor
    
    # el ultimo
    jscab={}
    jscab["nombre"] = idcargo
    jscab["valor"] = totalcargo
    jscab["detalle"] = listadetalle

    listacargos.append(jscab)

    contexto = {
        "liquidacion" : liquidacion,
        "detalle" : listacargos,
        "nombre_dc": dc.ctdescripcionenreporte,
        "nombre_gao": gao.ctdescripcionenreporte,
        "nombre_gaoa": gaoa.ctdescripcionenreporte
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="liquidacion "' + str(liquidacion.cxliquidacion) + ".pdf"
    # find the template and render it.
    template = get_template(template_name)
    html = template.render(contexto)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def ImpresionRecuperacionProtesto(request, cobranza_id):
    detalle = {}
    template_path = 'cobranzas/recuperacion_protesto_reporte.html'
    forma_cobro = ''
    datos_deposito='N/A'
    codigo_forma = ''
    fecha_protesto=''
    motivo_protesto=''
    nd_protesto = 0

    # tomar el codigo de asignacion grabado en la solicitud
    recuperacion = Recuperaciones_cabecera.objects.filter(id= cobranza_id).first()
    
    if not recuperacion:
        return HttpResponse("no encontró cobranza ")

    # cuando la forma de pago es DEP es deposito de accesorios y de ahí debe
    # tomar la fecha de vencimiento
    detalle = Recuperaciones_detalle.objects\
        .filter(recuperacion = cobranza_id, leliminado = False)\
        .order_by('chequeprotestado')


    codigo_forma = recuperacion.cxformacobro

    # cargar forma de cobro
    if recuperacion.cxformacobro=="MOV":
        forma_cobro = 'Movimiento contable'
    else:
        if recuperacion.lpagadoporelcliente:
                forma_cobro = 'Cliente '
        else:
                forma_cobro = 'Deudor '

    if recuperacion.cxformacobro=="EFE":
        forma_cobro += "paga en efectivo"
    if recuperacion.cxformacobro=="TRA":
        forma_cobro += 'transfiere de ' + recuperacion.cxcuentatransferencia.__str__()
    if recuperacion.cxformacobro=="CHE":
        forma_cobro += 'emite cheque ' + recuperacion.cxcheque.__str__()
    
    if recuperacion.cxformacobro != "MOV":
        datos_deposito = recuperacion.ddeposito.strftime("%Y/%m/%d")

        if recuperacion.ldepositoencuentaconjunta:
                datos_deposito += ' en cuenta del cliente'
        else:
                datos_deposito += ' en ' + recuperacion.cxcuentadeposito.__str__()

    # totales
    tot_cobro = detalle.aggregate(Sum('nvalorrecuperacion'))
    tot_bajas = detalle.aggregate(Sum('nvalorbaja'))
    tot_bajascobranza = detalle.aggregate(Sum('nvalorbajacobranza'))

    totales = {
        "cobrado":tot_cobro["nvalorrecuperacion__sum"]
        , "bajas":tot_bajas["nvalorbaja__sum"]
                +tot_bajascobranza["nvalorbajacobranza__sum"]
        , "aplicado":tot_cobro["nvalorrecuperacion__sum"]
                +tot_bajas["nvalorbaja__sum"]
                +tot_bajascobranza["nvalorbajacobranza__sum"]
    }

    # crear un objeto json agrupando los cobros por protesto y que haya un elemento
    # json que contenga el detalle de cada cobranza.
    idprotesto=""
    totalrecuperado = 0
    fechaprotesto =''
    motivoprotesto=''
    valorprotesto=0
    saldoprotesto=0
    listadetalle = []
    listaprotestos=[]

    for i in range(len(detalle)):
        item = detalle[i]

        if idprotesto != item.documentoprotestado.chequeprotestado.__str__() and idprotesto !="":
            
            jscab={}
            jscab["nombre"] = idprotesto
            jscab["valor_aplicado"] = totalrecuperado 
            jscab["fecha"] = fechaprotesto
            jscab["motivo"] = motivoprotesto
            jscab["valor_protesto"] = valorprotesto
            jscab["saldo_protesto"] = saldoprotesto
            jscab["detalle"] = listadetalle

            listaprotestos.append(jscab)

            totalrecuperado=0
            jsdet={}
            listadetalle = []

        idprotesto = item.documentoprotestado.chequeprotestado.__str__() 

        jsdet={}
        jsdet["asignacion"] = item.documentoprotestado.documento.cxasignacion
        jsdet["documento"] = item.documentoprotestado.documento.ctdocumento
        jsdet["vencimiento"] = item.vencimiento()
        jsdet["dias_vencidos"] = item.dias_vencidos()
        jsdet["saldo_al_dia_protesto"] = item.nsaldoaldia
        jsdet["saldo_al_dia_baja_cobranza"] = item.nsaldoaldiabajacobranza
        jsdet["valor_recuperado"] = item.nvalorrecuperacion
        jsdet["valor_baja"]=item.nvalorbaja + item.nvalorbajacobranza
        jsdet["total_aplicado"]=item.aplicado()
        jsdet["saldo_actual_protesto"] = item.documentoprotestado.nsaldo

        listadetalle.append(jsdet)

        totalrecuperado += item.nvalorrecuperacion + item.nvalorbaja
        # datos del protesto para guardar
        fechaprotesto = item.documentoprotestado.chequeprotestado.dprotesto
        motivoprotesto = item.documentoprotestado.chequeprotestado.motivoprotesto.ctmotivoprotesto
        valorprotesto = item.documentoprotestado.chequeprotestado.nvalor
        saldoprotesto = item.documentoprotestado.chequeprotestado.nsaldo
    
    # el ultimo
    jscab={}
    jscab["nombre"] = idprotesto
    jscab["valor_aplicado"] = totalrecuperado
    jscab["fecha"] = fechaprotesto
    jscab["motivo"] = motivoprotesto
    jscab["valor_protesto"] = valorprotesto
    jscab["saldo_protesto"] = saldoprotesto
    jscab["detalle"] = listadetalle

    listaprotestos.append(jscab)

    # si cobranza esta protstada, enviar datos del protestp
    if recuperacion.cxestado=='P':
        cheque = Cheques.objects.filter(pk = recuperacion.cxcheque.id).first()
        protesto = Cheques_protestados.objects.filter(cheque = cheque).first()
        if protesto:
            fecha_protesto = protesto.dprotesto
            motivo_protesto = protesto.motivoprotesto.ctmotivoprotesto
            nd_protesto = protesto.nvalornotadebito


    context = {
        "cobranza" : recuperacion,
        "detalle" : listaprotestos,
        "datos_forma_cobro" : forma_cobro,
        "datos_deposito" : datos_deposito,
        "forma_cobro": codigo_forma,
        "totales": totales,
        "fecha_protesto": fecha_protesto,
        "motivo_protesto": motivo_protesto,
        "nd_protesto":nd_protesto,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="cobranza "' + str(recuperacion.cxrecuperacion) + ".pdf"
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

def ImpresionCobranzaCargos(request, cobranza_id):
    detalle = {}
    template_path = 'cobranzas/cobranzas_cargos_reporte.html'
    forma_cobro = ''
    datos_deposito='N/A'
    codigo_forma = ''
    cobranza = Cargos_cabecera.objects.filter(id= cobranza_id).first()
    
    if not cobranza:
        return HttpResponse("no encontró cobranza ")

    detalle = Cargos_detalle.objects\
        .filter(cxcobranza = cobranza_id, leliminado = False)

    codigo_forma = cobranza.cxformapago

    # cargar forma de cobro
    if cobranza.cxformapago=="MOV":
        forma_cobro = 'Movimiento contable'
    else:
        # if cobranza.lpagadoporelcliente:
                forma_cobro = 'Cliente '
        # else:
                # forma_cobro = 'Deudor '

    if cobranza.cxformapago=="EFE":
        forma_cobro += "paga en efectivo"
    if cobranza.cxformapago=="TRA":
        forma_cobro += 'transfiere de ' + cobranza.cxcuentatransferencia.__str__()
    if cobranza.cxformapago=="CHE":
        forma_cobro += 'emite cheque ' + cobranza.cxcheque.__str__()
    
    if cobranza.cxformapago != "MOV":
        datos_deposito = cobranza.ddeposito.strftime("%Y/%m/%d")

        # if cobranza.ldepositoencuentaconjunta:
        #         datos_deposito += ' en cuenta del cliente'
        # else:
        datos_deposito += ' en ' + cobranza.cxcuentadeposito.__str__()

    # totales
    tot_cobro = detalle.aggregate(Sum('nvalorcobranza'))

    totales = {
        "cobrado":tot_cobro["nvalorcobranza__sum"]
        , "aplicado":tot_cobro["nvalorcobranza__sum"]
    }

    context = {
        "cobranza" : cobranza,
        "detalle" : detalle,
        "datos_forma_cobro" : forma_cobro,
        "datos_deposito" : datos_deposito,
        "forma_cobro": codigo_forma,
        "totales": totales,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="cobranza "' + str(cobranza.cxcobranza) + ".pdf"
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

