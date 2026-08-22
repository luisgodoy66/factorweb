import os
from decimal import Decimal
from email.utils import parseaddr
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

from django.db import transaction

from empresa.models import Tipos_factoring, Contador, Datos_participantes
from solicitudes.models import Asignacion, Clientes, Documentos
from clientes.models import Datos_compradores


try:
    from lxml import etree as lxml_etree
except ImportError:  # pragma: no cover - dependency optional
    lxml_etree = None


DEFAULT_XSD_PATH = Path(__file__).resolve().parent.parent / 'factura_V2.1.0.xsd'
INICIAL_SOLICITUD = 'sol'


def _normalizar_texto(value) -> str:
    return (value or '').strip()


def _normalizar_email(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    _, address = parseaddr(value)
    return address.lower().strip() if address else None


def _buscar_hijo(elemento, nombre):
    if elemento is None:
        return None
    for child in elemento:
        if child.tag == nombre:
            return child
    return None


def _texto(elemento, nombre, default=''):
    child = _buscar_hijo(elemento, nombre)
    if child is None or child.text is None:
        return default
    return _normalizar_texto(child.text)


def _decimal(texto, default=Decimal('0')):
    texto = _normalizar_texto(texto)
    if not texto:
        return default
    try:
        return Decimal(texto)
    except Exception:
        return default


def _fecha(texto, default=None):
    texto = _normalizar_texto(texto)
    if not texto:
        return default
    for formato in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            from datetime import datetime
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return default


def _extraer_xml_factura(xml_content):
    """Devuelve el XML de factura, incluso si viene envuelto en <autorizacion>/<comprobante>."""
    xml_texto = xml_content.decode('utf-8', errors='ignore') if isinstance(xml_content, bytes) else str(xml_content)
    xml_texto = xml_texto.strip().lstrip('\ufeff')

    root = ET.fromstring(xml_texto)
    tag_raiz = root.tag.split('}')[-1].lower()
    if tag_raiz == 'factura':
        return xml_texto

    if tag_raiz == 'autorizacion':
        comprobante = root.find('comprobante') or root.find('{*}comprobante')
        if comprobante is None or not comprobante.text:
            print("El XML de autorizacion no contiene comprobante con factura")
            raise ValueError('El XML de autorizacion no contiene comprobante con factura')
        factura_xml = comprobante.text.strip().lstrip('\ufeff')
        # ET entrega CDATA como texto plano; al reparsear validamos que sea una factura.
        factura_root = ET.fromstring(factura_xml)
        if factura_root.tag.split('}')[-1].lower() != 'factura':
            print("El comprobante no contiene un XML de factura valido")
            raise ValueError('El comprobante no contiene un XML de factura valido')
        return factura_xml

    raise ValueError('El XML no corresponde a una factura ni a una autorizacion SRI')


def validar_xml_con_xsd(xml_content, xsd_path=None):
    """Valida el XML contra el XSD adjunto cuando lxml está disponible."""
    if not xsd_path:
        xsd_path = DEFAULT_XSD_PATH
    if not xsd_path or not os.path.exists(xsd_path):
        print(f"No se encontró el archivo XSD en {xsd_path}, no se puede validar el XML contra el XSD")
        return True

    if lxml_etree is None:
        print("lxml no está disponible, no se puede validar el XML contra el XSD")
        return True
    parser = lxml_etree.XMLParser(remove_blank_text=True)
    xml_doc = lxml_etree.fromstring(xml_content.encode('utf-8') if isinstance(xml_content, str) else xml_content, parser=parser)
    schema_doc = lxml_etree.parse(str(xsd_path), parser=parser)
    schema = lxml_etree.XMLSchema(schema_doc)
    schema.assertValid(xml_doc)
    print("XML validado correctamente contra el XSD")
    return True


def parsear_factura_xml(xml_content, xsd_path=None):
    """Parsea un XML de factura al formato esperado por los modelos."""
    factura_xml = _extraer_xml_factura(xml_content)
    validar_xml_con_xsd(factura_xml, xsd_path=xsd_path)

    root = ET.fromstring(factura_xml.encode('utf-8'))
    info_tributaria = root.find('infoTributaria') or root.find('{*}infoTributaria')
    info_factura = root.find('infoFactura') or root.find('{*}infoFactura')
    detalles = root.find('detalles') or root.find('{*}detalles')

    if info_tributaria is None or info_factura is None:
        raise ValueError('El XML no tiene la estructura esperada: falta infoTributaria o infoFactura')

    estab = _texto(info_tributaria, 'estab')
    pto_emi = _texto(info_tributaria, 'ptoEmi')
    secuencial = _texto(info_tributaria, 'secuencial')
    clave_acceso = _texto(info_tributaria, 'claveAcceso')

    total_sin_impuestos = _decimal(_texto(info_factura, 'totalSinImpuestos'))
    total_descuento = _decimal(_texto(info_factura, 'totalDescuento'))
    importe_total = _decimal(_texto(info_factura, 'importeTotal'))

    total_impuestos = Decimal('0')
    total_con_impuestos = info_factura.find('totalConImpuestos') or info_factura.find('{*}totalConImpuestos')
    if total_con_impuestos is not None:
        for imp in total_con_impuestos.findall('totalImpuesto') or total_con_impuestos.findall('{*}totalImpuesto'):
            valor = _decimal(_texto(imp, 'valor'))
            total_impuestos += valor

    if importe_total == Decimal('0'):
        importe_total = total_sin_impuestos + total_impuestos

    fecha_emision = _fecha(_texto(info_factura, 'fechaEmision'))
    fecha_vencimiento = fecha_emision

    razon_comprador = _texto(info_factura, 'razonSocialComprador')
    identificacion_comprador = _texto(info_factura, 'identificacionComprador')

    descripcion = ''
    cantidad = Decimal('0')
    precio_unitario = Decimal('0')
    if detalles is not None:
        detalle = detalles.find('detalle') or detalles.find('{*}detalle')
        if detalle is not None:
            descripcion = _texto(detalle, 'descripcion')
            cantidad = _decimal(_texto(detalle, 'cantidad'))
            precio_unitario = _decimal(_texto(detalle, 'precioUnitario'))

    return {
        'serie1': estab,
        'serie2': pto_emi,
        'documento': secuencial,
        'fecha_emision': fecha_emision,
        'fecha_vencimiento': fecha_vencimiento,
        'valor_antes_iva': total_sin_impuestos,
        'iva': total_impuestos if total_impuestos else max(importe_total - total_sin_impuestos - total_descuento, Decimal('0')),
        'total': importe_total,
        'clave_acceso': clave_acceso,
        'comprador_nombre': razon_comprador,
        'comprador_identificacion': identificacion_comprador,
        'descripcion': descripcion,
        'cantidad': cantidad,
        'precio_unitario': precio_unitario,
    }


def encontrar_cliente_por_remitente(sender_email, empresa=None):
    """Busca el cliente por el email del remitente usando ctemail2."""
    email = _normalizar_email(sender_email)
    if not email:
        return None

    qs = Clientes.objects.filter(leliminado=False)
    if empresa is not None:
        qs = qs.filter(empresa=empresa)

    return qs.filter(ctemail2__iexact=email)\
        .order_by('-dregistro').first() or qs.filter(ctemail__iexact=email).order_by('-dregistro').first()


def _crear_documento_desde_datos(datos, asignacion, empresa, user):
    from datetime import date, timedelta

    fecha = datos['fecha_emision'] or date.today()
    fecha_vencimiento = date.today() + timedelta(days=30)

    return Documentos.objects.create(
        empresa=empresa,
        cxusuariocrea=user,
        cxusuariomodifica=user.id,
        cxasignacion=asignacion,
        cxcomprador=datos['comprador_identificacion'][:13],
        ctcomprador=datos['comprador_nombre'][:100],
        ctserie1=datos['serie1'][:3],
        ctserie2=datos['serie2'][:3],
        ctdocumento=datos['documento'][:9],
        demision=fecha,
        dvencimiento=fecha_vencimiento,
        nvalorantesiva=datos['valor_antes_iva'],
        niva=datos['iva'],
        ntotal=datos['total'],
        cxautorizacion_ec=datos['clave_acceso'][:49],
    )


def crear_asignacion_desde_xmls(xml_contents, sender_email, empresa, user, tipo_factoring=None, asunto=None, xsd_path=None):
    """Crea una sola asignación y un documento por cada XML recibido."""
    if not xml_contents:
        raise ValueError('No se recibieron facturas XML')

    cliente = encontrar_cliente_por_remitente(sender_email, empresa=empresa)
    if cliente is None:
        raise ValueError('No se encontró un cliente para el remitente {}'.format(sender_email))

    if tipo_factoring is None:
        tipo_factoring = Tipos_factoring.objects.filter(
            empresa=empresa, leliminado=False
        ).order_by('dregistro').first()
    if tipo_factoring is None:
        raise ValueError('No existe un tipo de factoring configurado para la empresa')

    datos_facturas = [parsear_factura_xml(xml, xsd_path=xsd_path) for xml in xml_contents]
    total_lote = sum((datos['total'] for datos in datos_facturas), Decimal('0'))
    ruc = cliente.cxcliente

    with transaction.atomic():
        # Buscar una asignación existente para el cliente y tipo de 
        # factoring, si no existe, crear una nueva
        asignacion = Asignacion.objects.filter(
            empresa=empresa,
            cxcliente=cliente,
            cxtipo='F',
            cxestado='P',
            leliminado=False,
        ).first()

        if asignacion is None:
            secuencia = Contador.objects\
                .filter(
                    empresa=empresa,
                    cxtransaccion=INICIAL_SOLICITUD + ruc,
            ).first()
            if secuencia is None:
                secuencia = Contador.objects.create(
                    empresa=empresa,
                    cxusuariocrea=user,
                    cxtransaccion=INICIAL_SOLICITUD + ruc,
                    nultimonumero=1,
                )
            else:
                secuencia.nultimonumero += 1
                secuencia.save(update_fields=['nultimonumero'])

            numero_solicitud = INICIAL_SOLICITUD + str(secuencia.nultimonumero).zfill(5)
            
            asignacion = Asignacion.objects.create(
                cxcliente=cliente,
                cxtipofactoring=tipo_factoring,
                cxtipo='F',
                nvalor=Decimal('0'),
                ncantidaddocumentos=0,
                cxusuariocrea=user,
                empresa=empresa,
                cxasignacion=numero_solicitud,
            )

        documentos = [
            _crear_documento_desde_datos(datos, asignacion, empresa, user)
            for datos in datos_facturas
        ]
        asignacion.nvalor = (asignacion.nvalor or Decimal('0')) + total_lote
        asignacion.ncantidaddocumentos = (asignacion.ncantidaddocumentos or 0) + len(documentos)
        asignacion.save(update_fields=['nvalor', 'ncantidaddocumentos'])

        for documento in documentos:
            # grabar comprador , si es nuevo
            datosparticipante = Datos_participantes.objects\
                .filter(cxparticipante = documento.cxcomprador if documento else None,
                        empresa = empresa).first()
            
            if not datosparticipante:

                cxtipoid = documento.cxtipoid if documento else None

                datosparticipante=Datos_participantes(
                    cxtipoid = cxtipoid,
                    cxparticipante = documento.cxcomprador if documento else None,
                    ctnombre = documento.ctcomprador if documento else None,
                    cxusuariocrea = user,
                    empresa = empresa,
                )
                if datosparticipante:
                    datosparticipante.save()

            comprador = Datos_compradores.objects\
                .filter(cxcomprador = datosparticipante.id)\
                    .first()

            if not comprador:
                comprador=Datos_compradores(
                    cxcomprador = datosparticipante,
                    cxusuariocrea = user,
                    empresa = empresa
                )
                if comprador:
                    comprador.save()

            # grabar eºl código del comprador en la factura
            documento.comprador = comprador
            documento.save()

    return {
        'cliente': cliente,
        'asignacion': asignacion,
        'documentos': documentos,
        'datos': datos_facturas,
    }


def crear_asignacion_desde_xml(xml_content, sender_email, empresa, user, tipo_factoring=None, asunto=None, xsd_path=None):
    """Mantiene la API individual y delega en el procesamiento por lote."""
    return crear_asignacion_desde_xmls(
        [xml_content], sender_email, empresa, user, tipo_factoring, asunto, xsd_path
    )


def procesar_mensaje_del_agente(correo_data, empresa, user, tipo_factoring=None, xsd_path=None):
    """Procesa un correo ya leído por un agente IA y sus adjuntos XML."""
    sender_email = correo_data.get('from') or correo_data.get('sender') or correo_data.get('sender_email') or ''
    asunto = correo_data.get('subject') or correo_data.get('asunto') or ''
    attachments = correo_data.get('attachments') or correo_data.get('adjuntos') or []
    if not attachments:
        return {'procesados': 0, 'creadas': 0, 'resultados': [], 'correos': [], 'msg': 'No hay adjuntos para procesar'}

    if not isinstance(attachments, list):
        attachments = [attachments]

    xml_contents = []
    for attachment in attachments:
        if isinstance(attachment, dict):
            xml_content = attachment.get('content') or attachment.get('xml') or attachment.get('data') or ''
        else:
            xml_content = attachment
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode('utf-8', errors='ignore')
        xml_content = str(xml_content) if xml_content else ''
        if '<' not in xml_content or '</' not in xml_content:
            continue
        xml_contents.append(xml_content)

    if not xml_contents:
        return {'procesados': 0, 'creadas': 0, 'resultados': [], 'correos': [], 'msg': 'No se encontraron XML válidos'}

    try:
        resultado = crear_asignacion_desde_xmls(
            xml_contents=xml_contents,
            sender_email=sender_email,
            empresa=empresa,
            user=user,
            tipo_factoring=tipo_factoring,
            asunto=asunto,
            xsd_path=xsd_path,
        )
    except (ValueError, ET.ParseError):
        return {'procesados': 0, 'creadas': 0, 'resultados': [], 'correos': [], 'msg': 'Error al procesar el XML'}

    return {
        'procesados': 1,
        'creadas': len(resultado['documentos']),
        'resultados': [resultado],
        'correos': [{
            'from': sender_email,
            'subject': asunto,
            'creadas': len(resultado['documentos']),
            'attachments': len(xml_contents),
        }],
    }

