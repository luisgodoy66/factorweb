"""Pruebas de la autenticacion de webhooks con claves por empresa.

Cubre `empresa.Claves_webhook` y el helper `empresa.claves`:
  - clave valida -> resuelve la empresa duena
  - clave invalida / inactiva / expirada / eliminada -> rechazo
  - cabeceras X-Margarita-Key y X-Margarita-API-Key
  - clave global de entorno (compatibilidad hacia atras)
  - aislamiento multi-tenant: la empresa de la clave prevalece sobre el
    empresa_id del cuerpo

Ejecutar con:
    python manage.py test empresa.tests_seguridad \
        --settings=factorweb25.test_settings_min
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from bases.models import Empresas
from empresa.claves import (
    LONGITUD_PREFIJO,
    resolver_empresa_webhook,
    validar_clave_webhook,
)
from empresa.models import Claves_webhook


class BaseClavesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='tester', password='x', is_superuser=True)
        self.empresa_a = Empresas.objects.create(
            ctnombre='FACTOR A', ctruccompania='0993220167001')
        self.empresa_b = Empresas.objects.create(
            ctnombre='FACTOR B', ctruccompania='0993230707001')

    def crear_clave(self, empresa, **kwargs):
        """Crea una clave y devuelve (instancia, clave_en_texto_plano)."""
        clave = Claves_webhook(
            ctnombre=kwargs.pop('ctnombre', 'n8n'),
            cxusuariocrea=self.user,
            empresa=empresa,
            **kwargs)
        plana = clave.generar_clave()
        clave.save()
        return clave, plana

    def peticion(self, clave=None, cabecera='X-Margarita-Key', **extra):
        headers = {}
        if clave is not None:
            headers['HTTP_' + cabecera.upper().replace('-', '_')] = clave
        return self.factory.post('/cualquier/', data={}, **headers, **extra)


class ClaveValidaTests(BaseClavesTests):
    def test_clave_valida_resuelve_la_empresa_duena(self):
        _clave, plana = self.crear_clave(self.empresa_a)
        empresa_id, clave_usada, error = validar_clave_webhook(
            self.peticion(plana))
        self.assertIsNone(error)
        self.assertEqual(empresa_id, self.empresa_a.id)
        self.assertIsNotNone(clave_usada)

    def test_clave_de_empresa_b_resuelve_empresa_b(self):
        _clave, plana = self.crear_clave(self.empresa_b)
        empresa_id, _, error = validar_clave_webhook(self.peticion(plana))
        self.assertIsNone(error)
        self.assertEqual(empresa_id, self.empresa_b.id)

    def test_se_acepta_la_cabecera_alterna(self):
        _clave, plana = self.crear_clave(self.empresa_a)
        empresa_id, _, error = validar_clave_webhook(
            self.peticion(plana, cabecera='X-Margarita-API-Key'))
        self.assertIsNone(error)
        self.assertEqual(empresa_id, self.empresa_a.id)

    def test_se_registra_el_ultimo_uso(self):
        clave, plana = self.crear_clave(self.empresa_a)
        self.assertIsNone(clave.dultimouso)
        validar_clave_webhook(self.peticion(plana))
        clave.refresh_from_db()
        self.assertIsNotNone(clave.dultimouso)

    def test_el_prefijo_permite_identificar_la_clave(self):
        clave, plana = self.crear_clave(self.empresa_a)
        self.assertEqual(clave.ctprefijo, plana[:LONGITUD_PREFIJO])
        self.assertEqual(len(clave.ctprefijo), LONGITUD_PREFIJO)

    def test_la_clave_no_se_guarda_en_texto_plano(self):
        clave, plana = self.crear_clave(self.empresa_a)
        self.assertNotEqual(clave.ctclavehash, plana)
        self.assertNotIn(plana, clave.ctclavehash)


class ClaveInvalidaTests(BaseClavesTests):
    def test_sin_cabecera_se_rechaza(self):
        empresa_id, _, error = validar_clave_webhook(self.peticion())
        self.assertIsNone(empresa_id)
        self.assertIn('X-Margarita-Key', error)

    def test_clave_incorrecta_se_rechaza(self):
        self.crear_clave(self.empresa_a)
        empresa_id, _, error = validar_clave_webhook(
            self.peticion('clave_que_no_existe'))
        self.assertIsNone(empresa_id)
        self.assertEqual(error, 'clave invalida')

    def test_clave_ajena_con_mismo_prefijo_se_rechaza(self):
        """Dos claves con el mismo prefijo no deben confundirse."""
        _c, plana_a = self.crear_clave(self.empresa_a)
        _c2, plana_b = self.crear_clave(self.empresa_b)
        # la verificacion es por hash, no por prefijo
        empresa_id, _, error = validar_clave_webhook(self.peticion(plana_a))
        self.assertIsNone(error)
        self.assertEqual(empresa_id, self.empresa_a.id)

    def test_clave_inactiva_se_rechaza(self):
        clave, plana = self.crear_clave(self.empresa_a)
        clave.lactiva = False
        clave.save()
        empresa_id, _, error = validar_clave_webhook(self.peticion(plana))
        self.assertIsNone(empresa_id)

    def test_clave_eliminada_se_rechaza(self):
        clave, plana = self.crear_clave(self.empresa_a)
        clave.leliminado = True
        clave.save()
        empresa_id, _, error = validar_clave_webhook(self.peticion(plana))
        self.assertIsNone(empresa_id)

    def test_clave_expirada_se_rechaza(self):
        clave, plana = self.crear_clave(
            self.empresa_a,
            dexpiracion=timezone.now().date() - timedelta(days=1))
        self.assertFalse(clave.esta_vigente())
        empresa_id, _, error = validar_clave_webhook(self.peticion(plana))
        self.assertIsNone(empresa_id)

    def test_clave_vigente_hasta_hoy_se_acepta(self):
        _clave, plana = self.crear_clave(
            self.empresa_a, dexpiracion=timezone.now().date())
        empresa_id, _, error = validar_clave_webhook(self.peticion(plana))
        self.assertIsNone(error)
        self.assertEqual(empresa_id, self.empresa_a.id)

    def test_clave_corta_no_rompe(self):
        self.crear_clave(self.empresa_a)
        empresa_id, _, error = validar_clave_webhook(self.peticion('abc'))
        self.assertIsNone(empresa_id)

    def test_clave_sin_hash_no_rompe(self):
        Claves_webhook.objects.create(
            ctnombre='sin hash', ctprefijo='12345678', ctclavehash='',
            cxusuariocrea=self.user, empresa=self.empresa_a)
        empresa_id, _, error = validar_clave_webhook(self.peticion('12345678xx'))
        self.assertIsNone(empresa_id)


class ClaveGlobalTests(BaseClavesTests):
    """Compatibilidad con la clave global de entorno."""

    def test_clave_global_se_acepta_y_no_fija_empresa(self):
        from django.conf import settings
        empresa_id, clave_usada, error = validar_clave_webhook(
            self.peticion(settings.INTERNAL_API_KEY))
        self.assertIsNone(error)
        self.assertIsNone(empresa_id)
        self.assertIsNone(clave_usada)

    def test_clave_global_no_es_valida_como_clave_de_empresa(self):
        self.crear_clave(self.empresa_a)
        from django.conf import settings
        empresa_id, _, error = validar_clave_webhook(
            self.peticion(settings.INTERNAL_API_KEY))
        self.assertIsNone(empresa_id)
        self.assertIsNone(error)


class AislamientoMultiTenantTests(BaseClavesTests):
    """La empresa de la clave debe prevalecer sobre el empresa_id del cuerpo."""

    def test_la_empresa_de_la_clave_prevalece(self):
        _clave, plana = self.crear_clave(self.empresa_a)
        # el atacante pide la empresa B, pero su clave es de la empresa A
        empresa, error = resolver_empresa_webhook(
            self.peticion(plana), empresa_solicitada=self.empresa_b.id)
        self.assertIsNone(error)
        self.assertEqual(empresa.id, self.empresa_a.id)

    def test_la_empresa_de_la_clave_prevalece_sobre_empresa_inexistente(self):
        _clave, plana = self.crear_clave(self.empresa_a)
        empresa, error = resolver_empresa_webhook(
            self.peticion(plana), empresa_solicitada=999999)
        self.assertIsNone(error)
        self.assertEqual(empresa.id, self.empresa_a.id)

    def test_clave_global_respeta_el_empresa_id_del_cuerpo(self):
        from django.conf import settings
        empresa, error = resolver_empresa_webhook(
            self.peticion(settings.INTERNAL_API_KEY),
            empresa_solicitada=self.empresa_b.id)
        self.assertIsNone(error)
        self.assertEqual(empresa.id, self.empresa_b.id)

    def test_clave_global_sin_empresa_id_falla(self):
        from django.conf import settings
        empresa, error = resolver_empresa_webhook(
            self.peticion(settings.INTERNAL_API_KEY))
        self.assertIsNone(empresa)
        self.assertIn('empresa_id', error)

    def test_clave_invalida_no_resuelve_empresa(self):
        self.crear_clave(self.empresa_a)
        empresa, error = resolver_empresa_webhook(
            self.peticion('clave_mala'), empresa_solicitada=self.empresa_b.id)
        self.assertIsNone(empresa)
        self.assertEqual(error, 'clave invalida')

    def test_empresa_eliminada_de_la_clave_no_resuelve(self):
        clave, plana = self.crear_clave(self.empresa_a)
        self.empresa_a.delete()
        empresa, error = resolver_empresa_webhook(self.peticion(plana))
        self.assertIsNone(empresa)
