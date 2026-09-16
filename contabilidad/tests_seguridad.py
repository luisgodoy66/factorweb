"""Tests de seguridad del endpoint de asientos contables (hallazgo H3).

Ejecutar con:
    python manage.py test contabilidad.tests_seguridad
"""
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.permissions import IsAuthenticated

from .views import asiento_contable_api


@override_settings(ALLOWED_HOSTS=['testserver'])
class AsientoContableApiTests(TestCase):
    """El asiento contable no debe exponerse de forma anonima ni cross-tenant."""

    def test_exige_autenticacion(self):
        self.assertIn(IsAuthenticated, asiento_contable_api.cls.permission_classes)

    def test_acceso_anonimo_devuelve_403(self):
        url = reverse('contabilidad:asiento_contable_api', args=[1])
        respuesta = self.client.get(url, secure=True)
        self.assertIn(respuesta.status_code, (401, 403))

    def test_la_vista_filtra_por_empresa(self):
        import inspect

        fuente = inspect.getsource(asiento_contable_api)
        self.assertIn('empresa=id_empresa.empresa', fuente)
        self.assertIn('IsAuthenticated', fuente)
