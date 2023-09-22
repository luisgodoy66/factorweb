# import xml.etree.cElementTree as etree
import xml.etree.ElementTree as etree
import time
import os
import io

from django.shortcuts import redirect, HttpResponse
from decimal import Decimal

from .models import Impuestos_facturaventa, Items_facturaventa, Factura_venta\
    , Diario_cabecera

def GeneraXMLFactura(request, ids_facturas, ambiente):
    # clave de acceso
    ids = ids_facturas.split(',')
    for id_factura in ids:

        factura = Factura_venta.objects.get(pk = id_factura)
        claveacceso = time.strftime('%d%m%Y',time.strptime(str(factura.demision), '%Y-%m-%d')) \
            + '01' +factura.empresa.ctruccompania + ambiente \
            + factura.puntoemision.cxestablecimiento \
            + factura.puntoemision.cxpuntoemision\
            + factura.cxnumerofactura.zfill(9) \
            + factura.cxnumerofactura.zfill(8) + '1'
        dv = calculate_check_digit(claveacceso)        

        claveacceso += str(dv)

        # crear el XML y bajarlo a la carpeta descargas
        documento = etree.Element('factura')
        documento.set('id','comprobante')
        documento.set('version','1.1.0')

        # generar infoTributaria
        infoTributaria = _get_tax_element(factura, claveacceso, ambiente)
        documento.append(infoTributaria)
        
        # generar infoFactura
        infoFactura = _get_invoice_element(factura)
        documento.append(infoFactura)
        
        #generar detalles
        detalles = _get_detail_element(factura)        
        documento.append(detalles)

        # informacion adicional
        concepto = Diario_cabecera.objects.filter(id = factura.asiento.id).first()
        infoAdicional = etree.Element('infoAdicional')
        campoAdicional = etree.SubElement(infoAdicional,'campoAdicional')
        campoAdicional.text=concepto.ctconcepto
        campoAdicional.set('nombre','Concepto')
        
        documento.append(infoAdicional)

        tree = etree.ElementTree(documento)

        # # Set the path for the Downloads folder
        # folder = os.path.join(os.path.expanduser("~"), "Downloads")

        # # Set the full path for the file
        # file_path = os.path.join(folder, claveacceso+".XML")

        # tree.write(claveacceso+".XML")

        try:
            
            # return generar_xml(request)
            return bajararchivo(request, tree ,claveacceso+".XML")
        except TypeError as err:
            return HttpResponse("Se ha producido en error en la generación del archivo.{}".format(err))
    
    # SIGUIENDO el formato de las rtinas fetch, debo devolver 'OK' primero
    # return HttpResponse( "OK"+str(factura.asiento.id))
    return HttpResponse( "OK")

def bajararchivo(request,tree, nombrearchivo):
    # Save document to memory and download to the user's browser
    # tree.write(claveacceso+".XML")
    tree = tree.getroot()
    document_data = etree.tostring(tree)
    # document_data.seek(0)
    response = HttpResponse(document_data,content_type="application/xml",)
    response["Content-Disposition"] = 'attachment; filename = "' + nombrearchivo 
    return response                

def _get_tax_element( invoice, access_key, ambiente):
    """
    """
    company = invoice.empresa
    infoTributaria = etree.Element('infoTributaria')
    etree.SubElement(infoTributaria, 'ambiente').text = ambiente
    etree.SubElement(infoTributaria, 'tipoEmision').text = '1'
    etree.SubElement(infoTributaria, 'razonSocial').text = company.ctnombre
    etree.SubElement(infoTributaria, 'nombreComercial').text = company.ctnombre
    etree.SubElement(infoTributaria, 'ruc').text = company.ctruccompania
    etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
    etree.SubElement(infoTributaria, 'codDoc').text = invoice.cxtipodocumento
    etree.SubElement(infoTributaria, 'estab').text = invoice.puntoemision.cxestablecimiento
    etree.SubElement(infoTributaria, 'ptoEmi').text = invoice.puntoemision.cxpuntoemision
    etree.SubElement(infoTributaria, 'secuencial').text = invoice.cxnumerofactura.zfill(9)
    etree.SubElement(infoTributaria, 'dirMatriz').text = company.ctdireccion
    return infoTributaria

tipoIdentificacion = {
    'R' : '04',
    'C' : '05',
    'P' : '06',
    'O' : '08',
}

codigoImpuesto = {
    'IVA': '2',
    'ICE': '3',
    'IRB': '5'
}

tarifaImpuesto = {
    '0': '0',
    '12.00': '2',
    '14.00': '3',
    'N/A': '6',
    'EXE': '7',
}

def _get_invoice_element( invoice):
    """
    """
    company = invoice.empresa
    cliente = invoice.cliente.cxcliente
    tsi = Decimal(invoice.nbaseiva) + Decimal(invoice.nbasenoiva)
    infoFactura = etree.Element('infoFactura')
    etree.SubElement(infoFactura, 'fechaEmision').text = time.strftime('%d/%m/%Y',time.strptime(str(invoice.demision), '%Y-%m-%d'))
    etree.SubElement(infoFactura, 'dirEstablecimiento').text = invoice.puntoemision.ctdireccion
    if int(company.ctcontribuyenteespecial) >0:
        etree.SubElement(infoFactura, 'contribuyenteEspecial').text = company.ctcontribuyenteespecial
    etree.SubElement(infoFactura, 'obligadoContabilidad').text = 'SI'
    etree.SubElement(infoFactura, 'tipoIdentificacionComprador').text = tipoIdentificacion[cliente.cxtipoid]
    etree.SubElement(infoFactura, 'razonSocialComprador').text = cliente.ctnombre
    etree.SubElement(infoFactura, 'identificacionComprador').text = cliente.cxparticipante
    etree.SubElement(infoFactura, 'totalSinImpuestos').text = '%.2f' % (tsi)
    etree.SubElement(infoFactura, 'totalDescuento').text = '%.2f' % (0.00)
    
    #totalConImpuestos
    totalConImpuestos = etree.Element('totalConImpuestos')
    imp = Impuestos_facturaventa.objects.filter(factura = invoice.id)
    if imp:
        for tax in imp:

            totalImpuesto = etree.Element('totalImpuesto')
            etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto[tax.cximpuesto]
            etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax.cxporcentaje]
            etree.SubElement(totalImpuesto, 'baseImponible').text = '{:.2f}'.format(tax.nbase)
            etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(tax.nvalor)
            totalConImpuestos.append(totalImpuesto)
    else:            
            totalImpuesto = etree.Element('totalImpuesto')
            etree.SubElement(totalImpuesto, 'codigo').text = '2'
            etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = '0'
            etree.SubElement(totalImpuesto, 'baseImponible').text = '{:.2f}'.format(invoice.nbaseiva)
            etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(0)
            totalConImpuestos.append(totalImpuesto)
            
    infoFactura.append(totalConImpuestos)
    
    etree.SubElement(infoFactura, 'propina').text = '0.00'
    etree.SubElement(infoFactura, 'importeTotal').text = str(invoice.nvalor)
    etree.SubElement(infoFactura, 'moneda').text = 'DOLAR'
        
    pagos = etree.Element('pagos')
    pago = etree.Element('pago')
    etree.SubElement(pago,'formaPago').text = "15"
    etree.SubElement(pago,'total').text = str(invoice.nvalor)
    pagos.append(pago)
    infoFactura.append(pagos)
    return infoFactura

def _get_refund_element(self, refund, invoice):
    """
    """
    company = refund.company_id
    partner = refund.partner_id
    infoNotaCredito = etree.Element('infoNotaCredito')
    etree.SubElement(infoNotaCredito, 'fechaEmision').text = time.strftime('%d/%m/%Y',time.strptime(refund.date_invoice, '%Y-%m-%d'))
    etree.SubElement(infoNotaCredito, 'dirEstablecimiento').text = company.street2
    etree.SubElement(infoNotaCredito, 'tipoIdentificacionComprador').text = tipoIdentificacion[partner.type_ced_ruc]
    etree.SubElement(infoNotaCredito, 'razonSocialComprador').text = partner.name
    etree.SubElement(infoNotaCredito, 'identificacionComprador').text = partner.ced_ruc
    etree.SubElement(infoNotaCredito, 'contribuyenteEspecial').text = company.company_registry
    etree.SubElement(infoNotaCredito, 'obligadoContabilidad').text = 'SI'
    etree.SubElement(infoNotaCredito, 'codDocModificado').text = '01'
    etree.SubElement(infoNotaCredito, 'numDocModificado').text = invoice[0].supplier_invoice_number
    etree.SubElement(infoNotaCredito, 'fechaEmisionDocSustento').text = time.strftime('%d/%m/%Y',time.strptime(invoice[0].date_invoice, '%Y-%m-%d'))
    etree.SubElement(infoNotaCredito, 'totalSinImpuestos').text = '%.2f' % (refund.amount_untaxed)
    etree.SubElement(infoNotaCredito, 'valorModificacion').text = '%.2f' % (refund.amount_untaxed)
    etree.SubElement(infoNotaCredito, 'moneda').text = 'DOLAR'
    
    #totalConImpuestos
    totalConImpuestos = etree.Element('totalConImpuestos')
    for tax in refund.tax_line:

        if tax.tax_group in ['vat', 'vat0', 'ice', 'other']:
            totalImpuesto = etree.Element('totalImpuesto')
            etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto[tax.tax_group]
            etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax.tax_group]
            etree.SubElement(totalImpuesto, 'baseImponible').text = '{:.2f}'.format(tax.base_amount)
            etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(tax.tax_amount)
            totalConImpuestos.append(totalImpuesto)
            
    infoNotaCredito.append(totalConImpuestos)
    etree.SubElement(infoNotaCredito, 'motivo').text = refund.origin
    return infoNotaCredito
    
def _get_detail_element( invoice):
    """
    """
    detalles = etree.Element('detalles')
    items = Items_facturaventa.objects.filter(factura = invoice.id)

    for line in items:
        detalle = etree.Element('detalle')
        etree.SubElement(detalle, 'codigoPrincipal').text = line.item.cxmovimiento
        etree.SubElement(detalle, 'descripcion').text = line.item.ctmovimiento
        etree.SubElement(detalle, 'cantidad').text = '%.6f' % (1)
        etree.SubElement(detalle, 'precioUnitario').text = '%.6f' % (line.nvalor)
        etree.SubElement(detalle, 'descuento').text = '%.2f' % (0)
        etree.SubElement(detalle, 'precioTotalSinImpuesto').text = '%.2f' % (line.nvalor)
        impuestos = etree.Element('impuestos')

        impuesto = etree.Element('impuesto')
        etree.SubElement(impuesto, 'codigo').text = codigoImpuesto['IVA']
        if line.lcargaiva:
            etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto[str(invoice.nporcentajeiva)]
            etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (Decimal(invoice.nporcentajeiva))
            etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.nvalor)
            etree.SubElement(impuesto, 'valor').text = '%.2f' % (line.nvalor * Decimal(invoice.nporcentajeiva) / 100)
        else:
            etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto["0"]
            etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (0)
            etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.nvalor)
            etree.SubElement(impuesto, 'valor').text = '%.2f' % (0)
        impuestos.append(impuesto)

        detalle.append(impuestos)
        detalles.append(detalle)
    return detalles

def _get_detail_element_refund(self, invoice):
    """
    """
    detalles = etree.Element('detalles')
    for line in invoice.invoice_line:
        detalle = etree.Element('detalle')
        etree.SubElement(detalle, 'codigoInterno').text = line.product_id.default_code
        if line.product_id.manufacturer_pref:
            etree.SubElement(detalle, 'codigoAdicional').text = line.product_id.manufacturer_pref
        etree.SubElement(detalle, 'descripcion').text = line.product_id.name
        etree.SubElement(detalle, 'cantidad').text = '%.6f' % (line.quantity)
        etree.SubElement(detalle, 'precioUnitario').text = '%.6f' % (line.price_unit)
        etree.SubElement(detalle, 'descuento').text = '%.2f' % (line.discount_value)
        etree.SubElement(detalle, 'precioTotalSinImpuesto').text = '%.2f' % (line.price_subtotal)
        impuestos = etree.Element('impuestos')
        for tax_line in line.invoice_line_tax_id:
            if tax_line.tax_group in ['vat', 'vat0', 'ice', 'other']:
                impuesto = etree.Element('impuesto')
                etree.SubElement(impuesto, 'codigo').text = codigoImpuesto[tax_line.tax_group]
                etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax_line.tax_group]
                etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (tax_line.amount * 100)
                etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.price_subtotal)
                etree.SubElement(impuesto, 'valor').text = '%.2f' % (line.amount_tax)
                impuestos.append(impuesto)
        detalle.append(impuestos)
        detalles.append(detalle)
    return detalles

def calculate_check_digit(number):
    # Convert the number to a list of integers
    digits = [int(d) for d in str(number)]
    # Calculate the weighted sum of the digits
    # weighted_sum = sum((len(digits) + 1 - i) * d for i, d in enumerate(digits))
    weighted_sum = 0
    i = len(digits)
    while i>0:
        # iterar de 2 al 7 usando sentencia for?
        for j in range(2,8):
            weighted_sum += digits[i-1] * j
            i -=1

    # Calculate the remainder when dividing the weighted sum by 11
    remainder = weighted_sum % 11
    # Calculate the check digit
    check_digit = (11 - remainder) % 10
    return check_digit

