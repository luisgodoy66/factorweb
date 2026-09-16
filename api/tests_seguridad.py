"""Tests de seguridad de los endpoints expuestos por la app api.

Cubren el hallazgo H2 (endpoints /api/* anonimos) y H5 (webhooks entrantes
sin verificacion de firma).

Ejecutar con:
    python manage.py test api.tests_seguridad
"""
import hashlib
import hmac
import json

from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from rest_framework.permissions import IsAuthenticated

from .views import (
    ConsultarFacturaAI,
    InvoiceAIAnalysisView,
    estado_operativo_cliente_api,
)


@override_settings(ALLOWED_HOSTS=['testserver'])
class EndpointsPrivadosTests(TestCase):
    """Los endpoints DRF no deben ser accesibles sin sesion."""

    def test_estado_operativo_cliente_exige_autenticacion(self):
        self.assertIn(IsAuthenticated, estado_operativo_cliente_api.cls.permission_classes)

    def test_invoice_ai_analysis_exige_autenticacion(self):
        self.assertIn(IsAuthenticated, InvoiceAIAnalysisView.permission_classes)

    def test_consultar_factura_ai_exige_autenticacion(self):
        self.assertIn(IsAuthenticated, ConsultarFacturaAI.cls.permission_classes)

    def test_acceso_anonimo_devuelve_403(self):
        for url in (
            reverse('api:estado_operativo_cliente_api', args=[1]),
            reverse('api:invoice-ai-analysis', args=[1]),
            reverse('api:consultar-factura-ai', args=[1]),
        ):
            with self.subTest(url=url):
                respuesta = self.client.get(url, secure=True)
                self.assertIn(respuesta.status_code, (401, 403))

    def test_default_de_drf_es_autenticado(self):
        self.assertEqual(
            settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'],
            ['rest_framework.permissions.IsAuthenticated'],
        )
        self.assertIn('rest_framework', settings.INSTALLED_APPS)


@override_settings(ALLOWED_HOSTS=['testserver'])
class WebhookTwilioTests(TestCase):
    """El webhook de Twilio debe rechazar todo lo que no venga firmado."""

    TOKEN = 'token_de_prueba'

    def setUp(self):
        from api.models import Configuracion_twilio_whatsapp

        self.configuracion = Configuracion_twilio_whatsapp(
            ctdescripcion='prueba',
            ctaccountsid='ACprueba',
            ctauthtoken=self.TOKEN,
            ctwhatsappnumber='+593999999999',
            lactivo=True,
            empresa_id=1,
        )
        self.url = reverse('api:webhook_whatsapp_twilio')
        self.factory = RequestFactory()

    def _peticion(self, datos, firma=None):
        extra = {'HTTP_HOST': 'testserver'}
        if firma is not None:
            extra['HTTP_X_TWILIO_SIGNATURE'] = firma
        return self.factory.post(self.url, datos, **extra)

    def test_sin_cabecera_de_firma_se_rechaza(self):
        from api.twilio_service import _firma_twilio_valida

        ok, motivo = _firma_twilio_valida(self._peticion({'From': 'whatsapp:+593'}), self.configuracion)
        self.assertFalse(ok)
        self.assertIn('X-Twilio-Signature', motivo)

    def test_firma_valida_se_acepta(self):
        from api.twilio_service import _firma_twilio_valida
        from twilio.request_validator import RequestValidator

        datos = {'From': 'whatsapp:+593999999999', 'Body': 'hola', 'MessageSid': 'SM1'}
        url_publica = 'http://testserver' + self.url
        firma = RequestValidator(self.TOKEN).compute_signature(url_publica, datos)

        ok, motivo = _firma_twilio_valida(self._peticion(datos, firma), self.configuracion)
        self.assertTrue(ok, motivo)

    def test_cuerpo_manipulado_se_rechaza(self):
        from api.twilio_service import _firma_twilio_valida
        from twilio.request_validator import RequestValidator

        original = {'From': 'whatsapp:+593999999999', 'Body': 'hola', 'MessageSid': 'SM1'}
        url_publica = 'http://testserver' + self.url
        firma = RequestValidator(self.TOKEN).compute_signature(url_publica, original)

        manipulado = dict(original, Body='otro cuerpo')
        ok, _ = _firma_twilio_valida(self._peticion(manipulado, firma), self.configuracion)
        self.assertFalse(ok)


@override_settings(ALLOWED_HOSTS=['testserver'])
class WebhookMetaWhatsAppTests(TestCase):
    """El webhook de Meta debe validar X-Hub-Signature-256."""

    def _peticion(self, cuerpo, firma=None):
        extra = {}
        if firma is not None:
            extra['HTTP_X_HUB_SIGNATURE_256'] = firma
        return RequestFactory().post(
            '/api/whatsapp/webhook/', data=cuerpo,
            content_type='application/json', **extra
        )

    def test_sin_firma_se_rechaza(self):
        from api.whatsapp import _firma_meta_valida

        ok, motivo = _firma_meta_valida(self._peticion(b'{"entry": []}'))
        self.assertFalse(ok)
        self.assertIn('X-Hub-Signature-256', motivo)

    def test_firma_correcta_se_acepta(self):
        from api.whatsapp import _firma_meta_valida

        secreto = settings.WHATSAPP_APP_SECRET
        if not secreto:
            self.skipTest('WHATSAPP_APP_SECRET no configurado')

        cuerpo = b'{"entry": []}'
        firma = 'sha256=' + hmac.new(
            secreto.encode(), cuerpo, hashlib.sha256
        ).hexdigest()
        ok, motivo = _firma_meta_valida(self._peticion(cuerpo, firma))
        self.assertTrue(ok, motivo)

    def test_cuerpo_manipulado_se_rechaza(self):
        from api.whatsapp import _firma_meta_valida

        secreto = settings.WHATSAPP_APP_SECRET
        if not secreto:
            self.skipTest('WHATSAPP_APP_SECRET no configurado')

        firma = 'sha256=' + hmac.new(
            secreto.encode(), b'{"entry": []}', hashlib.sha256
        ).hexdigest()
        ok, _ = _firma_meta_valida(self._peticion(b'{"entry": ["alterado"]}', firma))
        self.assertFalse(ok)

    def test_webhook_anonimo_devuelve_403(self):
        respuesta = self.client.post(
            '/api/whatsapp/webhook/', data=json.dumps({'entry': []}),
            content_type='application/json', secure=True
        )
        self.assertEqual(respuesta.status_code, 403)
