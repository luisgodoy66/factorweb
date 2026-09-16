"""Tests de seguridad del alta de asignaciones con accesorios (hallazgo H1)
y del webhook de carga de solicitudes (hallazgo H5).

Ejecutar con:
    python manage.py test solicitudes.tests_seguridad
"""
import ast
import json
import os

from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .webhooks import _clave_webhook_valida

RUTA_VIEWS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views.py')


def _parsear_cheques(lista):
    """Replica exacta del parseo seguro usado en DatosAsignacionConAccesorios."""
    try:
        if not lista:
            raise ValueError('vacio')
        salida = json.loads(lista)
    except (ValueError, TypeError):
        try:
            salida = ast.literal_eval(lista) if lista else []
        except (ValueError, SyntaxError, TypeError):
            salida = []

    if not isinstance(salida, list):
        salida = []
    return [elem for elem in salida if isinstance(elem, dict)]


class SinEvalTests(TestCase):
    """El modulo de vistas no debe contener llamadas a eval()/exec()."""

    def test_no_hay_llamadas_a_eval_ni_exec(self):
        with open(RUTA_VIEWS, encoding='utf-8') as archivo:
            arbol = ast.parse(archivo.read())

        peligrosas = [
            (nodo.func.id, nodo.lineno)
            for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.Call)
            and isinstance(nodo.func, ast.Name)
            and nodo.func.id in ('eval', 'exec')
        ]
        self.assertEqual(peligrosas, [], 'Hay llamadas a eval()/exec(): %s' % peligrosas)


class ParseoChequesTests(TestCase):
    """El payload de cheques debe parsearse sin ejecutar codigo."""

    def test_payload_json_valido(self):
        payload = json.dumps([{'banco': 1, 'cheque': '001', 'valor': 100.5}])
        self.assertEqual(len(_parsear_cheques(payload)), 1)

    def test_literal_con_comillas_simples(self):
        self.assertEqual(len(_parsear_cheques("[{'banco': 1, 'cheque': '001'}]")), 1)

    def test_codigo_arbitrario_no_se_ejecuta(self):
        self.assertEqual(_parsear_cheques('__import__("os").system("echo pwned")'), [])

    def test_lista_vacia_es_valida(self):
        self.assertEqual(_parsear_cheques('[]'), [])

    def test_parametro_ausente_no_rompe(self):
        self.assertEqual(_parsear_cheques(None), [])
        self.assertEqual(_parsear_cheques(''), [])

    def test_elementos_no_diccionario_se_descartan(self):
        self.assertEqual(_parsear_cheques('[1, 2, "texto", null]'), [])

    def test_objeto_en_lugar_de_lista_se_descarta(self):
        self.assertEqual(_parsear_cheques('{"banco": 1}'), [])


@override_settings(ALLOWED_HOSTS=['testserver'])
class WebhookSolicitudesTests(TestCase):
    """El webhook de carga de solicitudes debe exigir clave compartida."""

    def setUp(self):
        self.url = reverse('solicitudes:webhook_cargar_facturas')
        self.factory = RequestFactory()

    def _peticion(self, clave=None, cabecera='X-Margarita-Key'):
        extra = {}
        if clave is not None:
            # RequestFactory usa el nombre de cabecera con guiones -> guiones_bajos
            extra['HTTP_' + cabecera.upper().replace('-', '_')] = clave
        return self.factory.post(
            self.url, data=json.dumps({'correo': {}}),
            content_type='application/json', **extra
        )

    def test_sin_clave_se_rechaza(self):
        ok, motivo = _clave_webhook_valida(self._peticion())
        self.assertFalse(ok)
        self.assertIn('X-Margarita-Key', motivo)

    def test_clave_incorrecta_se_rechaza(self):
        ok, _ = _clave_webhook_valida(self._peticion('clave_incorrecta'))
        self.assertFalse(ok)

    def test_clave_correcta_se_acepta(self):
        clave = settings.MARGARITA_API_KEY
        if not clave:
            self.skipTest('MARGARITA_API_KEY no configurada en el entorno')
        ok, motivo = _clave_webhook_valida(self._peticion(clave))
        self.assertTrue(ok, motivo)

    def test_clave_correcta_con_cabecera_alterna_se_acepta(self):
        """n8n puede enviar X-Margarita-API-Key; tambien debe funcionar."""
        clave = settings.MARGARITA_API_KEY
        if not clave:
            self.skipTest('MARGARITA_API_KEY no configurada en el entorno')
        ok, motivo = _clave_webhook_valida(
            self._peticion(clave, cabecera='X-Margarita-API-Key')
        )
        self.assertTrue(ok, motivo)

    def test_clave_incorrecta_con_cabecera_alterna_se_rechaza(self):
        ok, _ = _clave_webhook_valida(
            self._peticion('clave_incorrecta', cabecera='X-Margarita-API-Key')
        )
        self.assertFalse(ok)

    def test_webhook_anonimo_devuelve_403(self):
        respuesta = self.client.post(
            self.url, data=json.dumps({'correo': {}}),
            content_type='application/json', secure=True
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_peticion_http_con_cabecera_correcta_pasa_la_autenticacion(self):
        """Integracion real: debe superar el control de clave y fallar mas
        adelante por payload invalido (400), nunca por 403."""
        clave = settings.MARGARITA_API_KEY
        if not clave:
            self.skipTest('MARGARITA_API_KEY no configurada en el entorno')

        for cabecera in ('HTTP_X_MARGARITA_KEY', 'HTTP_X_MARGARITA_API_KEY'):
            with self.subTest(cabecera=cabecera):
                respuesta = self.client.post(
                    self.url, data=json.dumps({'correo': {}}),
                    content_type='application/json', secure=True, **{cabecera: clave}
                )
                self.assertNotEqual(respuesta.status_code, 403)

    def test_peticion_http_sin_cabecera_devuelve_403(self):
        respuesta = self.client.post(
            self.url, data=json.dumps({'correo': {}}),
            content_type='application/json', secure=True
        )
        self.assertEqual(respuesta.status_code, 403)
