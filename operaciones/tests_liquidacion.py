"""Pruebas del envio automatico del correo de liquidacion (A3).

Cubre el servicio `operaciones.servicios.enviar_liquidacion` y el webhook
`operaciones.webhooks.webhook_enviar_correo_liquidacion`.

El envio SMTP y la generacion del PDF se sustituyen por dobles, de modo que las
pruebas no necesitan red ni plantillas.

Ejecutar con:
    python manage.py test operaciones.tests_liquidacion \
        --settings=factorweb25.test_settings_operaciones
"""
import json
from unittest import mock

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from bases.models import Empresas, Usuario_empresa
from empresa.models import Claves_webhook, Tipos_factoring
from solicitudes.models import Asignacion, Clientes


class BaseLiquidacionTests(TestCase):
    """Datos minimos: empresa, usuario, cliente y una solicitud liquidada."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='tester', password='x', is_superuser=True)

        self.empresa = Empresas.objects.create(
            ctnombre='FACTOR A', ctruccompania='0993220167001')
        self.otra_empresa = Empresas.objects.create(
            ctnombre='FACTOR B', ctruccompania='0993230707001')

        Usuario_empresa.objects.create(user=self.user, empresa=self.empresa)

        # Tipos_factoring sobreescribe save() sin aceptar force_insert, asi que
        # no se puede usar objects.create(). Ademas su save() hace .upper() sobre
        # ctinicialesliquidacioncobranza, que hay que informar.
        self.tipo = Tipos_factoring(
            cttipofactoring='factoring', ctabreviacion='FAC', cxmoneda='USD',
            ctinicialesliquidacioncobranza='LC',
            cxusuariocrea=self.user, empresa=self.empresa)
        self.tipo.save()

        self.cliente = Clientes.objects.create(
            cxcliente='1790012345001', ctnombre='CLIENTE UNO',
            ctemail='cliente@example.com',
            cxusuariocrea=self.user, empresa=self.empresa)

        self.cliente_sin_email = Clientes.objects.create(
            cxcliente='1790012345002', ctnombre='CLIENTE SIN CORREO',
            ctemail=None, ctemail2=None,
            cxusuariocrea=self.user, empresa=self.empresa)

    def crear_asignacion(self, cliente=None, estado='L', empresa=None,
                        codigo='sol00001'):
        return Asignacion.objects.create(
            cxcliente=cliente or self.cliente,
            cxtipofactoring=self.tipo,
            cxtipo='F',
            cxestado=estado,
            cxasignacion=codigo,
            nvalor=1000,
            cxusuariocrea=self.user,
            empresa=empresa or self.empresa,
        )

    def crear_clave(self, empresa=None):
        clave = Claves_webhook(
            ctnombre='n8n', cxusuariocrea=self.user,
            empresa=empresa or self.empresa)
        plana = clave.generar_clave()
        clave.save()
        return clave, plana

    def peticion(self, cuerpo, clave=None):
        extra = {}
        if clave:
            extra['HTTP_X_MARGARITA_KEY'] = clave
        # La vista se invoca directamente, no via URLconf, asi que basta con
        # una ruta representativa (ROOT_URLCONF de la suite esta vacio).
        return self.factory.post(
            '/operaciones/webhook/enviar-correo-liquidacion/',
            data=json.dumps(cuerpo), content_type='application/json', **extra)

    def parchear_envio(self, ok=True, error=None):
        """Sustituye el PDF y el SMTP."""
        return (
            mock.patch('operaciones.servicios.enviar_correo_liquidacion',
                       return_value=(ok, error)),
            mock.patch('operaciones.reportes.generar_pdf_liquidacion_para_empresa',
                       return_value=('sol00001.pdf', b'%PDF-1.4 fake', None)),
        )


class ServicioEnvioTests(BaseLiquidacionTests):
    def test_envia_y_marca_la_solicitud(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion()
        self.assertFalse(asignacion.lliquidacionnotificada)

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertTrue(resultado['ok'], resultado['error'])
        self.assertEqual(resultado['destinatario'], 'cliente@example.com')
        self.assertFalse(resultado['ya_enviada'])
        enviar.assert_called_once()

        asignacion.refresh_from_db()
        self.assertTrue(asignacion.lliquidacionnotificada)
        self.assertIsNotNone(asignacion.dliquidacionnotificada)

    def test_no_reenvia_si_ya_fue_notificada(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion()
        asignacion.lliquidacionnotificada = True
        asignacion.save()

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertTrue(resultado['ok'])
        self.assertTrue(resultado['ya_enviada'])
        enviar.assert_not_called()

    def test_forzar_reenvia_aunque_ya_estuviera_notificada(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion()
        asignacion.lliquidacionnotificada = True
        asignacion.save()

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa,
                                           forzar=True)

        self.assertTrue(resultado['ok'])
        self.assertFalse(resultado['ya_enviada'])
        enviar.assert_called_once()

    def test_no_envia_si_el_cliente_no_tiene_correo(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion(cliente=self.cliente_sin_email)
        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertFalse(resultado['ok'])
        self.assertIn('correo', resultado['error'].lower())
        enviar.assert_not_called()
        asignacion.refresh_from_db()
        self.assertFalse(asignacion.lliquidacionnotificada)

    def test_usa_ctemail2_si_falta_el_principal(self):
        from operaciones.servicios import enviar_liquidacion

        self.cliente_sin_email.ctemail2 = 'alterno@example.com'
        self.cliente_sin_email.save()
        asignacion = self.crear_asignacion(cliente=self.cliente_sin_email)

        p1, p2 = self.parchear_envio()
        with p1, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertTrue(resultado['ok'], resultado['error'])
        self.assertEqual(resultado['destinatario'], 'alterno@example.com')

    def test_no_notifica_si_la_solicitud_no_esta_liquidada(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion(estado='P')
        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertFalse(resultado['ok'])
        self.assertIn('estado', resultado['error'])
        enviar.assert_not_called()

    def test_acepta_estado_aceptada(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion(estado='A')
        p1, p2 = self.parchear_envio()
        with p1, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)
        self.assertTrue(resultado['ok'], resultado['error'])

    def test_solicitud_inexistente(self):
        from operaciones.servicios import enviar_liquidacion

        resultado = enviar_liquidacion(999999, self.empresa)
        self.assertFalse(resultado['ok'])
        self.assertIn('No existe la solicitud', resultado['error'])

    def test_aislamiento_entre_empresas(self):
        """Una empresa no puede notificar la solicitud de otra."""
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion(empresa=self.otra_empresa)
        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertFalse(resultado['ok'])
        self.assertIn('No existe la solicitud', resultado['error'])
        enviar.assert_not_called()

    def test_fallo_de_smtp_no_marca_como_notificada(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion()
        p1, p2 = self.parchear_envio(ok=False, error='SMTP caido')
        with p1, p2:
            resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertFalse(resultado['ok'])
        self.assertEqual(resultado['error'], 'SMTP caido')
        asignacion.refresh_from_db()
        self.assertFalse(asignacion.lliquidacionnotificada)

    def test_error_de_pdf_no_envia(self):
        from operaciones.servicios import enviar_liquidacion

        asignacion = self.crear_asignacion()
        with mock.patch(
                'operaciones.reportes.generar_pdf_liquidacion_para_empresa',
                return_value=(None, None, 'falta tasa GAO')):
            with mock.patch(
                    'operaciones.servicios.enviar_correo_liquidacion') as enviar:
                resultado = enviar_liquidacion(asignacion.id, self.empresa)

        self.assertFalse(resultado['ok'])
        self.assertIn('PDF', resultado['error'])
        enviar.assert_not_called()


class WebhookTests(BaseLiquidacionTests):
    def test_sin_clave_se_rechaza(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        respuesta = webhook_enviar_correo_liquidacion(
            self.peticion({'asignacion_id': 1}))
        self.assertEqual(respuesta.status_code, 403)

    def test_clave_de_otra_empresa_no_ve_la_solicitud(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        asignacion = self.crear_asignacion(empresa=self.otra_empresa)
        _c, plana = self.crear_clave(empresa=self.empresa)

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_id': asignacion.id}, clave=plana))

        self.assertEqual(respuesta.status_code, 207)
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['fallidos'], 1)
        self.assertEqual(cuerpo['enviados'], 0)
        enviar.assert_not_called()

    def test_envio_correcto(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        asignacion = self.crear_asignacion()
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_id': asignacion.id}, clave=plana))

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = json.loads(respuesta.content)
        self.assertTrue(cuerpo['ok'])
        self.assertEqual(cuerpo['enviados'], 1)
        self.assertEqual(cuerpo['empresa'], 'FACTOR A')
        self.assertEqual(cuerpo['resultados'][0]['destinatario'],
                         'cliente@example.com')

    def test_varias_solicitudes(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        a1 = self.crear_asignacion(codigo='sol00001')
        a2 = self.crear_asignacion(codigo='sol00002')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_ids': [a1.id, a2.id]}, clave=plana))

        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 2)
        self.assertEqual(cuerpo['enviados'], 2)

    def test_ids_como_cadena_separada_por_comas(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        a1 = self.crear_asignacion(codigo='sol00001')
        a2 = self.crear_asignacion(codigo='sol00002')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_ids': '%s,%s' % (a1.id, a2.id)},
                              clave=plana))

        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 2)
        self.assertEqual(cuerpo['enviados'], 2)

    def test_sin_ids_devuelve_400(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        _c, plana = self.crear_clave()
        respuesta = webhook_enviar_correo_liquidacion(
            self.peticion({}, clave=plana))
        self.assertEqual(respuesta.status_code, 400)

    def test_segunda_llamada_no_duplica(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        asignacion = self.crear_asignacion()
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_id': asignacion.id}, clave=plana))
            respuesta2 = webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_id': asignacion.id}, clave=plana))

        self.assertEqual(enviar.call_count, 1)
        cuerpo = json.loads(respuesta2.content)
        self.assertEqual(cuerpo['ya_enviadas'], 1)
        self.assertEqual(cuerpo['enviados'], 0)

    def test_estado_207_si_alguno_falla(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        a1 = self.crear_asignacion(codigo='sol00001')
        a2 = self.crear_asignacion(cliente=self.cliente_sin_email,
                                   codigo='sol00002')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'asignacion_ids': [a1.id, a2.id]}, clave=plana))

        self.assertEqual(respuesta.status_code, 207)
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['enviados'], 1)
        self.assertEqual(cuerpo['fallidos'], 1)
        self.assertFalse(cuerpo['ok'])
