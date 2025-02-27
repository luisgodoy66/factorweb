from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render
from django.db.models import Sum, Case, When, FloatField, DecimalField, Q
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django_weasyprint import WeasyTemplateResponse

from .models import  Documentos_cabecera, Documentos_detalle, Liquidacion_cabecera\
        , Liquidacion_detalle, Recuperaciones_cabecera, Recuperaciones_detalle\
        , Cheques, Cheques_protestados, Cargos_cabecera, Cargos_detalle\
        , DebitosCuentasConjuntas, Pagare_cabecera, Pagare_detalle
from operaciones.models import Notas_debito_cabecera, Notas_debito_detalle
from bases.models import Usuario_empresa
from empresa.models import Tasas_factoring
from contabilidad.models import Factura_venta

from datetime import datetime
# # from xhtml2pdf import pisa
# from weasyprint import HTML, CSS

def ImpresionCobranzaCartera(request, cobranza_id):
    detalle = {}
    template_path = 'cobranzas/cobranzas_cartera_reporte.html'
    forma_cobro = ''
    datos_deposito='N/A'
    codigo_forma = ''
    fecha_protesto=''
    motivo_protesto=''
    nd_protesto = 0

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # tomar el codigo de asignacion grabado en la solicitud
    cobranza = Documentos_cabecera.objects.filter(id= cobranza_id).first()
    
    if not cobranza:
        return HttpResponse("no encontró cobranza ")

    # obtener el detalle de la cobranza ordenado por comprador
    detalle = Documentos_detalle.objects\
        .filter(cxcobranza = cobranza_id, leliminado = False)\
        .order_by('cxdocumento__cxcomprador')

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
        datos_deposito = cobranza.ddeposito.strftime("%Y-%m-%d")

        if cobranza.ldepositoencuentaconjunta:
                datos_deposito += ' en cuenta compartida ' + cobranza.cxcuentaconjunta.__str__()
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
        protesto = Cheques_protestados.objects.filter(cheque = cheque
                                                      , leliminado = False).first()
        if protesto:
            fecha_protesto = protesto.dprotesto
            motivo_protesto = protesto.motivoprotesto.ctmotivoprotesto
            if protesto.notadedebito:
                nd_protesto = protesto.notadedebito.nvalor
            else:
                nd_protesto = None
    print(detalle,detalle.count())
    context = {
        "cobranza" : cobranza,
        "detalle" : detalle,
        "x":detalle.count(),
        "datos_forma_cobro" : forma_cobro,
        "datos_deposito" : datos_deposito,
        "forma_cobro": codigo_forma,
        "totales": totales,
        "fecha_protesto": fecha_protesto,
        "motivo_protesto": motivo_protesto,
        "nd_protesto":nd_protesto,
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
    response['Content-Disposition'] = 'inline; filename="cobranza "' \
        + str(cobranza.cxcobranza) + ".pdf"
    return response

def ImpresionLiquidacion(request, liquidacion_id):
    template_path = 'cobranzas/liquidacion_reporte.html'

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    liquidacion = Liquidacion_cabecera.objects.filter(pk = liquidacion_id).first()

    detalle_cargos = Liquidacion_detalle.objects.filter(liquidacion = liquidacion)\
        .order_by('cargo__cxmovimiento__cxmovimiento')

    # datos de tasa gao/dc
    gao = Tasas_factoring.objects.filter(cxtasa="GAO"
                                         , empresa = id_empresa.empresa).first()
    if not gao:
        return HttpResponse("no encontró tasa de gao")

    dc = Tasas_factoring.objects.filter(cxtasa="DCAR"
                                        , empresa = id_empresa.empresa).first()
    if not dc:
        return HttpResponse("no encontró tasa de descuento de catera")

    gaoa = Tasas_factoring.objects.filter(cxtasa="GAOA"
                                          , empresa = id_empresa.empresa).first()
    if not gaoa:
        return HttpResponse("no encontró tasa de GAO adicional")

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

        if item.cxtipooperacion=="C":
            operacion = Documentos_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='R':
            operacion = Recuperaciones_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='D':
            operacion = Notas_debito_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='L':
            operacion = Liquidacion_cabecera.objects.filter(pk=item.operacion).first()
        elif item.cxtipooperacion =='F':
            nd = Notas_debito_cabecera.objects.filter(pk=item.operacion).first()
            operacion = Factura_venta.objects.filter(pk=nd.operacion).first()
        else:
             operacion = 'Tipo ' + item.cxtipooperacion + ' no definido'

        # el IVA no tiene documento, porque es general a la Liquidacion
        if item.cargo.cxasignacion != None:
            jsdet["asignacion"] = item.cargo.cxasignacion
            jsdet["documento"] = item.cargo.cxdocumento.ctdocumento
            jsdet["desembolso"] = item.cargo.cxasignacion.ddesembolso
        else:
        #     jsdet["asignacion"] = 'N/A'
            # cuando el tipo es D (nota de debito), se puede buscar si es de cuenta conjunta
            # y tomar el motivo para mostrarlo en el reporte
            # pero la busqueda es inversa ya que la id de la nd esta en la tabla de
            # debitos de cuentas controladas
            if item.cxtipooperacion=='D':
                ndb = DebitosCuentasConjuntas.objects.filter(notadedebito=operacion.id).first()
                if ndb:
                    jsdet["asignacion"] = 'N/A'
                    jsdet["documento"] = ndb.ctmotivo
                    jsdet["desembolso"] = ''

        jsdet["cobranza"] = operacion
        jsdet["valor_base"] = item.cargo.ctvalorbase
        jsdet["tasa_calculo"]=item.cargo.ntasacalculo
        jsdet["dias_calculo"] = item.cargo.ndiascalculo
        # jsdet["valor"] = item.cargo.nvalor
        jsdet["valor"] = item.nvalor

        listadetalle.append(jsdet)

        # totalcargo += item.cargo.nvalor
        totalcargo += item.nvalor
    
    # el ultimo
    jscab={}
    jscab["nombre"] = idcargo
    jscab["valor"] = totalcargo
    jscab["detalle"] = listadetalle

    listacargos.append(jscab)

    context = {
        "liquidacion" : liquidacion,
        "detalle" : listacargos,
        "nombre_dc": dc.ctdescripcionenreporte,
        "nombre_gao": gao.ctdescripcionenreporte,
        "nombre_gaoa": gaoa.ctdescripcionenreporte,
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
    response['Content-Disposition'] = 'inline; filename="liquidacion "' \
        + str(liquidacion.cxliquidacion) + ".pdf"
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

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # tomar el codigo de asignacion grabado en la solicitud
    recuperacion = Recuperaciones_cabecera.objects.filter(id= cobranza_id).first()
    
    if not recuperacion:
        return HttpResponse("no encontró cobranza ")

    # cuando la forma de pago es DEP es deposito de accesorios y de ahí DebitosCuentasConjuntase
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
                datos_deposito += ' en cuenta compartida ' + recuperacion.cxcuentaconjunta.__str__()
        else:
                datos_deposito += ' en ' + recuperacion.cxcuentadeposito.__str__()

    # totales
    tot_cobro = detalle.aggregate(Sum('nvalorrecuperacion'))
    tot_bajas = detalle.aggregate(Sum('nvalorbaja'))
    tot_bajascobranza = detalle.aggregate(Sum('nvalorbajacobranza'))

    totales = {
        "cobrado":tot_cobro["nvalorrecuperacion__sum"]
        , "bajas":tot_bajas["nvalorbaja__sum"]
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
        jsdet["valor_baja"]=item.nvalorbaja 
        jsdet["total_aplicado"]=item.aplicado()
        jsdet["saldo_actual_protesto"] = item.documentoprotestado.nsaldo

        listadetalle.append(jsdet)

        totalrecuperado += item.nvalorrecuperacion + item.nvalorbaja
        # datos del protesto para guardar
        fechaprotesto = item.documentoprotestado.chequeprotestado.dprotesto
        motivoprotesto = item.documentoprotestado.chequeprotestado.motivoprotesto.ctmotivoprotesto
        valorprotesto = item.documentoprotestado.chequeprotestado.nvalorcartera
        saldoprotesto = item.documentoprotestado.chequeprotestado.nsaldocartera
    
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
        protesto = Cheques_protestados.objects.filter(cheque = cheque
                                                      , leliminado = False).first()
        if protesto:
            fecha_protesto = protesto.dprotesto
            motivo_protesto = protesto.motivoprotesto.ctmotivoprotesto
            print(protesto.notadedebito)
            if protesto.notadedebito:
                nd_protesto = protesto.notadedebito.nvalor
            else:
                nd_protesto = None

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
    response['Content-Disposition'] = 'inline; filename="recuperacion "'\
          + str(recuperacion.cxrecuperacion) + ".pdf"
    return response    

def ImpresionCobranzaCargos(request, cobranza_id):
    detalle = {}
    template_path = 'cobranzas/cobranzas_cargos_reporte.html'
    forma_cobro = ''
    datos_deposito='N/A'
    codigo_forma = ''

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    cobranza = Cargos_cabecera.objects.filter(id= cobranza_id).first()
    
    if not cobranza:
        return HttpResponse("no encontró cobranza ")

    detalle = Cargos_detalle.objects\
        .filter(cxcobranza = cobranza_id)

    codigo_forma = cobranza.cxformapago

    # cargar forma de cobro
    if cobranza.cxformapago=="MOV":
        forma_cobro = 'Movimiento contable'
    else:
        forma_cobro = 'Cliente '

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
    response['Content-Disposition'] = 'inline; filename="cobranza "' \
        + str(cobranza.cxcobranza) + ".pdf"
    return response

def ImpresionProtestosPendientes(request, id_cliente = None):

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
     
    if id_cliente:         
        protestos = Cheques_protestados.objects\
            .protestos_pendientes_cliente(id_empresa.empresa, id_cliente)

        tot_cobro = Cheques_protestados.objects\
            .filter(empresa = id_empresa.empresa, leliminado = False
                    , nsaldocartera__gt=0, cheque__cxparticipante = id_cliente)\
                .aggregate(total_cartera = Sum('nvalorcartera')
                        , total_saldo = Sum('nsaldocartera'))

    else:
        protestos = Cheques_protestados.objects\
            .protestos_pendientes(id_empresa.empresa)

        # totalizar el campo nsaldocartera de la tabla cheques_protestados
        tot_cobro = Cheques_protestados.objects\
            .filter(empresa = id_empresa.empresa, leliminado = False, nsaldocartera__gt=0)\
                .aggregate(total_cartera = Sum('nvalorcartera')
                        , total_saldo = Sum('nsaldocartera'))

    template_path = 'cobranzas/protestos_reporte.html'

    context={
        "protestos" : protestos,
        "totales": tot_cobro,
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
    response['Content-Disposition'] = 'inline; filename="protestos_pendientes.pdf"'
    return response

from operaciones.models import Ampliaciones_plazo_cabecera, Ampliaciones_plazo_detalle \
, Documentos, ChequesAccesorios

def ImpresionAmpliacionDePlazo(request, ampliacion_id):
    template_path = 'cobranzas/ampliacion_de_plazo_reporte.html'

    id_empresa = Usuario_empresa.objects\
        .filter(user = request.user).first()
     
    ampliacion = Notas_debito_cabecera.objects\
        .filter(pk = ampliacion_id).first()

    ap = Ampliaciones_plazo_cabecera.objects\
        .filter(pk = ampliacion.operacion).first()

    detalle_ampliacion = Ampliaciones_plazo_detalle.objects\
        .filter(ampliacion = ampliacion.operacion)

    detalle_cargos = Notas_debito_detalle.objects\
        .filter(notadebito = ampliacion)\
        .order_by('cargo__cxmovimiento__ctmovimiento')

    listadocumentos = []
    documento=""
    hay_accesorios = False

    for i in range(len(detalle_ampliacion)):
        item = detalle_ampliacion[i]

        jsdet={}

        if item.cxtipoasignacion == 'F':
             doc = Documentos.objects.filter(pk = item.documentoaccesorio).first()
             documento = doc.__str__()
             asgn = doc.cxasignacion
             jsdet["Accesorio"] = None
        else:
             doc = ChequesAccesorios.objects.filter(pk = item.documentoaccesorio).first()
             documento = doc.documento.__str__()
             asgn = doc.documento.cxasignacion
             jsdet["Accesorio"] = doc.__str__()
             hay_accesorios=True

        jsdet["Asignacion"] = asgn
        jsdet["Documento"] = documento
        jsdet["AmpliarDesde"] = item.dampliaciondesde
        jsdet["Plazo"] = item.plazo
        jsdet["Cartera"] = item.nvalorcartera

        listadocumentos.append(jsdet)

    # datos de tasa gao/dc
    dc = Tasas_factoring.objects.filter(cxtasa="DCAR"
                                        , empresa = id_empresa.empresa).first()
    if not dc:
        return HttpResponse("no encontró tasa de descuento de catera")

    gaoa = Tasas_factoring.objects.filter(cxtasa="GAOA"
                                          , empresa = id_empresa.empresa).first()
    if not gaoa:
        return HttpResponse("no encontró tasa de GAO adicional")

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

        # el IVA no tiene documento, porque es general a la Liquidacion
        if item.cargo.cxasignacion != None:
            jsdet["asignacion"] = item.cargo.cxasignacion
            jsdet["documento"] = item.cargo.cxdocumento.ctdocumento
            jsdet["desembolso"] = item.cargo.cxasignacion.ddesembolso

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

    context = {
        "ampliacion" : ampliacion,
        "detalle" : listacargos,
        "nombre_dc": dc.ctdescripcionenreporte,
        "nombre_gaoa": gaoa.ctdescripcionenreporte,
        "ap" : ap,
        "detalle_ampliacion"  : listadocumentos,
        "hay_accesorios" : hay_accesorios,
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
    response['Content-Disposition'] = 'inline; filename="ampliacion "' \
        + str(ampliacion.cxnotadebito) + ".pdf"
    return response    

def ImpresionDetalleCobranzas(request, desde, hasta, clientes = None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    arr_clientes = []
    
    if clientes != None:
        ids = clientes.split(',')
        for id in ids:
            arr_clientes.append(id)
     
    template_path = 'cobranzas/detalle_cobranzas_reporte.html'

    if clientes == None:            
        detalle = Documentos_detalle.objects\
            .filter(cxcobranza__dcobranza__gte = desde,
                    cxcobranza__dcobranza__lte = hasta,
                    empresa = id_empresa.empresa,
                    leliminado = False)\
            .order_by('cxcobranza__cxcliente', 'cxcobranza__dcobranza')
    else:            
        detalle = Documentos_detalle.objects\
            .filter(cxcobranza__dcobranza__gte = desde,
                    cxcobranza__cxcliente__in = arr_clientes,
                    cxcobranza__dcobranza__lte = hasta,
                    empresa = id_empresa.empresa,
                    leliminado = False)\
            .order_by('cxcobranza__cxcliente', 'cxcobranza__dcobranza')
                    
    
    totales = detalle\
        .aggregate(cobrado = Sum(Case(
                                When( ~Q(cxcobranza__cxestado__in=['E','P'])
                                        , then='nvalorcobranza'),
                                default=0,
                                output_field=DecimalField(),)
                        ),
                    baja = Sum(Case(
                                When( ~Q(cxcobranza__cxestado__in=['E','P'])
                                        , then='nvalorbaja'),
                                default=0,
                                output_field=DecimalField(),)
                        ),
                    retenciones = Sum(Case(
                                When( ~Q(cxcobranza__cxestado__in=['E','P'])
                                        , then='nretenciones'),
                                default=0,
                                output_field=DecimalField(),)
                        ),
                    )

    context={
        'detalle':detalle,
        'total_cobrado' :totales['cobrado'] or 0,
        'total_retencionesybaja':totales['baja'] or 0 +totales['retenciones'] or 0,
        'total_general':totales['cobrado'] or 0 +totales['baja'] or 0 +totales['retenciones'] or 0,
        'empresa': id_empresa.empresa,
        'desde': datetime.strptime(desde, '%Y-%m-%d').date(),
        'hasta': datetime.strptime(hasta, '%Y-%m-%d').date(),
    }
    # Generar el archivo PDF usando WeasyTemplateResponse
    response = WeasyTemplateResponse(
        request=request,
        template=template_path,
        context=context,
        content_type='application/pdf',
        # stylesheets=stylesheet_paths
    )
    response['Content-Disposition'] = 'inline; filename="detalle_cobranzas.pdf"'
    return response    

def ImpresionDetalleRecuperaciones(request, desde, hasta, clientes = None):
    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()
    arr_clientes = []
    
    if clientes != None:
        ids = clientes.split(',')
        for id in ids:
            arr_clientes.append(id)
     
    template_path = 'cobranzas/detalle_recuperaciones_reporte.html'

    if clientes == None:            
        detalle = Recuperaciones_detalle.objects\
            .filter(recuperacion__dcobranza__gte = desde,
                    recuperacion__dcobranza__lte = hasta,
                    empresa = id_empresa.empresa,
                    leliminado = False)\
            .order_by('recuperacion__cxcliente', 'recuperacion__dcobranza')
    else:            
        detalle = Recuperaciones_detalle.objects\
            .filter(recuperacion__dcobranza__gte = desde,
                    recuperacion__dcobranza__lte = hasta,
                    recuperacion__cxcliente__in = arr_clientes,
                    empresa = id_empresa.empresa,
                    leliminado = False)\
            .order_by('recuperacion__cxcliente', 'recuperacion__dcobranza')
    
    totales = detalle\
        .aggregate(cobrado = Sum(Case(
                                When( ~Q(recuperacion__cxestado__in=['E','P'])
                                        , then='nvalorrecuperacion'),
                                default=0,
                                output_field=DecimalField(),)
                        ),
                    baja = Sum(Case(
                                When( ~Q(recuperacion__cxestado__in=['E','P'])
                                        , then='nvalorbaja'),
                                default=0,
                                output_field=DecimalField(),)
                        ),
                    bajacobranza = Sum(Case(
                                When( ~Q(recuperacion__cxestado__in=['E','P'])
                                        , then='nvalorbajacobranza'),
                                default=0,
                                output_field=DecimalField(),)
                        ),
                    )
    
    if not totales['cobrado']: totales['cobrado']=0
    if not totales['baja']: totales['baja']=0
    if not totales['bajacobranza']: totales['bajacobranza']=0
    
    context={
        'detalle':detalle,
        'total_cobrado' :totales['cobrado'],
        'total_baja':totales['baja']+totales["bajacobranza"],
        'total_general':totales['cobrado']+totales['baja']+totales["bajacobranza"],
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
    response['Content-Disposition'] = 'inline; filename="detalle_recuperaciones.pdf"'
    return response    

def ImpresionCobranzaCuota(request, cobranza_id):
    detalle = {}
    template_path = 'cobranzas/cobranzas_cuota_reporte.html'
    forma_cobro = ''
    datos_deposito='N/A'
    codigo_forma = ''
    fecha_protesto=''
    motivo_protesto=''
    nd_protesto = 0

    id_empresa = Usuario_empresa.objects.filter(user = request.user).first()

    # tomar el codigo de asignacion grabado en la solicitud
    cobranza = Pagare_cabecera.objects.filter(id= cobranza_id).first()
    
    if not cobranza:
        return HttpResponse("no encontró cobranza ")

    # cuando la forma de pago es DEP es deposito de accesorios y de ahí debe
    # tomar la fecha de vencimiento
    detalle = Pagare_detalle.objects\
        .filter(cobranza = cobranza_id, leliminado = False)

    codigo_forma = cobranza.cxformapago

    # cargar forma de cobro
    if cobranza.cxformapago=="MOV":
        forma_cobro = 'Movimiento contable'
    else:
        forma_cobro = 'Cliente '

    if cobranza.cxformapago=="EFE":
        forma_cobro += "paga en efectivo"
    if cobranza.cxformapago=="TRA":
        forma_cobro += 'transfiere de ' + cobranza.cxcuentatransferencia.__str__()
    if cobranza.cxformapago=="CHE":
        forma_cobro += 'emite cheque ' + cobranza.cxcheque.__str__()
    if cobranza.cxformapago=="DEP":
        forma_cobro = 'Se depositó accesorio ' + cobranza.cxcheque.__str__()
    
    if cobranza.cxformapago != "MOV":
        datos_deposito = cobranza.ddeposito.strftime("%Y-%m-%d")
        datos_deposito += ' en ' + cobranza.cxcuentadeposito.__str__()

    # totales
    tot_cobro = detalle.aggregate(Sum('nvalorcobranza'))

    totales = {
        "cobrado":tot_cobro["nvalorcobranza__sum"]
        , "aplicado":tot_cobro["nvalorcobranza__sum"]
    }

    # si cobranza esta protstada, enviar datos del protestp
    if cobranza.cxestado=='P':
        cheque = Cheques.objects.filter(pk = cobranza.cxcheque.id).first()
        protesto = Cheques_protestados.objects.filter(cheque = cheque
                                                      , leliminado = False).first()
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
    response['Content-Disposition'] = 'inline; filename="cobranza "' \
        + str(cobranza.cxcobranza) + ".pdf"
    return response
