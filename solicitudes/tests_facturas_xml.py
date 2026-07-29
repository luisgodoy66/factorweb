import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from bases.models import Empresas
from empresa.models import Tipos_factoring
from solicitudes.models import Asignacion, Clientes, Documentos
from solicitudes.servicios import crear_asignacion_desde_xml, encontrar_cliente_por_remitente
from solicitudes.views import webhook_cargar_solicitudes_factoring


class FacturasXmlTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='facturas-test', password='secret123')
        self.empresa = Empresas.objects.create(
            ctruccompania='0999999999001',
            ctnombre='Empresa Test',
            cxusuariomodifica=self.user.id,
        )
        self.tipo_factoring = Tipos_factoring.objects.create(
            empresa=self.empresa,
            cxusuariocrea=self.user,
            cttipofactoring='Factoring Test',
            ctabreviacion='FT',
            cxmoneda='USD',
        )
        self.cliente = Clientes.objects.create(
            empresa=self.empresa,
            cxusuariocrea=self.user,
            cxcliente='0999999999001',
            ctnombre='Cliente Test',
            ctemail2='facturas@example.com',
        )

    def test_encontrar_cliente_por_remitente(self):
        cliente = encontrar_cliente_por_remitente('FACTURAS@example.com', empresa=self.empresa)
        self.assertEqual(cliente, self.cliente)

    def test_crear_asignacion_desde_xml(self):
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <factura>
          <infoTributaria>
            <ambiente>1</ambiente>
            <tipoEmision>1</tipoEmision>
            <razonSocial>Empresa Test</razonSocial>
            <ruc>0999999999001</ruc>
            <claveAcceso>1234567890123456789012345678901234567890123</claveAcceso>
            <codDoc>01</codDoc>
            <estab>001</estab>
            <ptoEmi>001</ptoEmi>
            <secuencial>000000001</secuencial>
            <dirMatriz>Av. Principal</dirMatriz>
          </infoTributaria>
          <infoFactura>
            <fechaEmision>27/07/2026</fechaEmision>
            <tipoIdentificacionComprador>04</tipoIdentificacionComprador>
            <razonSocialComprador>Cliente Test</razonSocialComprador>
            <identificacionComprador>0999999999001</identificacionComprador>
            <totalSinImpuestos>100.00</totalSinImpuestos>
            <totalDescuento>0.00</totalDescuento>
            <totalConImpuestos>
              <totalImpuesto>
                <codigo>2</codigo>
                <codigoPorcentaje>2</codigoPorcentaje>
                <baseImponible>100.00</baseImponible>
                <valor>15.00</valor>
              </totalImpuesto>
            </totalConImpuestos>
            <importeTotal>115.00</importeTotal>
          </infoFactura>
          <detalles>
            <detalle>
              <descripcion>Servicio</descripcion>
              <cantidad>1.000000</cantidad>
              <precioUnitario>100.000000</precioUnitario>
              <descuento>0.00</descuento>
              <precioTotalSinImpuesto>100.00</precioTotalSinImpuesto>
              <impuestos>
                <impuesto>
                  <codigo>2</codigo>
                  <codigoPorcentaje>2</codigoPorcentaje>
                  <tarifa>15.00</tarifa>
                  <baseImponible>100.00</baseImponible>
                  <valor>15.00</valor>
                </impuesto>
              </impuestos>
            </detalle>
          </detalles>
        </factura>'''

        resultado = crear_asignacion_desde_xml(
            xml_content=xml_content,
            sender_email='facturas@example.com',
            empresa=self.empresa,
            user=self.user,
            tipo_factoring=self.tipo_factoring,
            asunto='Factura nueva',
        )

        self.assertEqual(resultado['cliente'], self.cliente)
        self.assertTrue(isinstance(resultado['asignacion'], Asignacion))
        self.assertEqual(resultado['asignacion'].cxcliente, self.cliente)
        self.assertEqual(resultado['asignacion'].nvalor, Decimal('115.00'))
        self.assertEqual(resultado['asignacion'].ncantidaddocumentos, 1)
        documento = resultado['documentos'][0]
        self.assertTrue(isinstance(documento, Documentos))
        self.assertEqual(documento.ctdocumento, '000000001')
        self.assertEqual(documento.ntotal, Decimal('115.00'))
        self.assertEqual(documento.nvalorantesiva, Decimal('100.00'))
        self.assertEqual(documento.niva, Decimal('15.00'))

    def test_webhook_carga_facturas_por_payload_del_agente(self):
        payload = {
            'correo': {
                'from': 'facturas@example.com',
                'subject': 'Factura nueva',
                'attachments': [
                    {'filename': 'factura.xml', 'content': '''<?xml version="1.0" encoding="UTF-8"?>
                    <factura>
                      <infoTributaria>
                        <ambiente>1</ambiente>
                        <tipoEmision>1</tipoEmision>
                        <razonSocial>Empresa Test</razonSocial>
                        <ruc>0999999999001</ruc>
                        <claveAcceso>1234567890123456789012345678901234567890123</claveAcceso>
                        <codDoc>01</codDoc>
                        <estab>001</estab>
                        <ptoEmi>001</ptoEmi>
                        <secuencial>000000001</secuencial>
                        <dirMatriz>Av. Principal</dirMatriz>
                      </infoTributaria>
                      <infoFactura>
                        <fechaEmision>27/07/2026</fechaEmision>
                        <tipoIdentificacionComprador>04</tipoIdentificacionComprador>
                        <razonSocialComprador>Cliente Test</razonSocialComprador>
                        <identificacionComprador>0999999999001</identificacionComprador>
                        <totalSinImpuestos>100.00</totalSinImpuestos>
                        <totalDescuento>0.00</totalDescuento>
                        <totalConImpuestos>
                          <totalImpuesto>
                            <codigo>2</codigo>
                            <codigoPorcentaje>2</codigoPorcentaje>
                            <baseImponible>100.00</baseImponible>
                            <valor>15.00</valor>
                          </totalImpuesto>
                        </totalConImpuestos>
                        <importeTotal>115.00</importeTotal>
                      </infoFactura>
                      <detalles>
                        <detalle>
                          <descripcion>Servicio</descripcion>
                          <cantidad>1.000000</cantidad>
                          <precioUnitario>100.000000</precioUnitario>
                          <descuento>0.00</descuento>
                          <precioTotalSinImpuesto>100.00</precioTotalSinImpuesto>
                          <impuestos>
                            <impuesto>
                              <codigo>2</codigo>
                              <codigoPorcentaje>2</codigoPorcentaje>
                              <tarifa>15.00</tarifa>
                              <baseImponible>100.00</baseImponible>
                              <valor>15.00</valor>
                            </impuesto>
                          </impuestos>
                        </detalle>
                      </detalles>
                    </factura>'''}
                ]
            }
        }

        request = self.factory.post(
            '/solicitudes/webhook/cargar-facturas/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        response = webhook_cargar_solicitudes_factoring(request)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertTrue(body['ok'])
        self.assertEqual(body['creadas'], 1)
        self.assertEqual(body['procesados'], 1)
