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
from clientes.models import Datos_generales
from empresa.models import Claves_webhook, Datos_participantes, Tipos_factoring
from solicitudes.models import Asignacion, Solicitantes


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

        self.solicitante = Solicitantes.objects.create(
            cxcliente='1790012345001', ctnombre='CLIENTE UNO',
            ctemail='cliente@example.com',
            cxusuariocrea=self.user, empresa=self.empresa)

        self.solicitante_sin_email = Solicitantes.objects.create(
            cxcliente='1790012345002', ctnombre='CLIENTE SIN CORREO',
            ctemail=None, ctemail2=None,
            cxusuariocrea=self.user, empresa=self.empresa)

        # El cliente del contrato (clientes.Datos_generales) es el que manda
        # para la notificacion; se enlaza OneToOne con Datos_participantes.
        # `_solicitante_de` guarda la pareja cliente -> solicitante para que
        # crear_asignacion no mezcle unos con otros.
        self._solicitante_de = {}

        self.cliente = self.crear_datos_generales(
            '1790012345001', 'CLIENTE UNO', 'cliente@example.com')
        self._solicitante_de[self.cliente.id] = self.solicitante

        # Cliente de contrato sin correo: su solicitante TAMPOCO tiene, para que
        # no lo rescate el respaldo por solicitante.
        self.solicitante_mudo = Solicitantes.objects.create(
            cxcliente='1790012345003', ctnombre='SOLICITANTE SIN CORREO',
            ctemail=None, ctemail2=None,
            cxusuariocrea=self.user, empresa=self.empresa)
        self.cliente_sin_email = self.crear_datos_generales(
            '1790012345004', 'CLIENTE SIN CORREO', None)
        self._solicitante_de[self.cliente_sin_email.id] = self.solicitante_mudo

        # Cliente cuyo correo solo esta en el campo alterno del solicitante.
        self.solicitante_alterno = Solicitantes.objects.create(
            cxcliente='1790012345005', ctnombre='SOLICITANTE ALTERNO',
            ctemail=None, ctemail2='alterno@example.com',
            cxusuariocrea=self.user, empresa=self.empresa)
        self.cliente_solo_alterno = self.crear_datos_generales(
            '1790012345006', 'CLIENTE ALTERNO', None)
        self._solicitante_de[self.cliente_solo_alterno.id] = \
            self.solicitante_alterno

    def crear_datos_generales(self, identificacion, nombre, email):
        participante = Datos_participantes.objects.create(
            cxtipoid='R', cxparticipante=identificacion, ctnombre=nombre,
            ctemail=email, cxusuariocrea=self.user, empresa=self.empresa)
        return Datos_generales.objects.create(
            cxcliente=participante, cxtipocliente='J',
            cxusuariocrea=self.user, empresa=self.empresa)

    def crear_asignacion(self, solicitante=None, cliente=None, estado='L',
                        empresa=None, codigo='sol00001'):
        cliente_final = cliente if cliente is not None else self.cliente
        # El solicitante debe ser el que corresponde a ese cliente de contrato;
        # si no se indica, se busca la pareja guardada en setUp.
        solicitante_final = (
            solicitante
            or self._solicitante_de.get(getattr(cliente_final, 'id', None))
            or self.solicitante
        )
        return Asignacion.objects.create(
            cxcliente=solicitante_final,
            cliente=cliente_final,
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

    def peticion_datos(self, parametros=None, clave=None, metodo='get'):
        """Peticion al endpoint de composicion (admite GET y POST)."""
        extra = {}
        if clave:
            extra['HTTP_X_MARGARITA_KEY'] = clave
        url = '/operaciones/webhook/datos-correo-liquidacion/'
        if metodo == 'post':
            return self.factory.post(
                url, data=json.dumps(parametros or {}),
                content_type='application/json', **extra)
        return self.factory.get(url, data=parametros or {}, **extra)

    def parchear_envio(self, ok=True, error=None):
        """Sustituye el PDF y el SMTP.

        enviar_correo_liquidacion se importa dentro de la funcion, asi que el
        parche debe apuntar al modulo donde se define (empresa.correos).
        """
        return (
            mock.patch('empresa.correos.enviar_correo_liquidacion',
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

        asignacion = self.crear_asignacion(cliente=self.cliente_solo_alterno)

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
                    'empresa.correos.enviar_correo_liquidacion') as enviar:
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


class ComposicionParaEnvioExternoTests(BaseLiquidacionTests):
    """Camino nuevo: Django compone, n8n envia (nodo nativo de Gmail).

    Resuelve el caso de Gmail, cuyo SMTP exige contrasena de aplicacion y
    rechaza el login con 534 5.7.9.
    """

    def test_compone_sin_enviar_y_sin_marcar(self):
        from operaciones.servicios import construir_correo_liquidacion

        asignacion = self.crear_asignacion()

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            correo = construir_correo_liquidacion(asignacion.id, self.empresa)

        self.assertTrue(correo['ok'], correo['error'])
        self.assertFalse(correo['ya_enviada'])
        self.assertEqual(correo['destinatario'], 'cliente@example.com')
        self.assertTrue(correo['asunto'])
        self.assertTrue(correo['cuerpo'])
        self.assertEqual(correo['pdf_nombre'], 'sol00001.pdf')
        # el PDF viaja en base64 para que n8n lo adjunte
        import base64 as _b64
        self.assertEqual(_b64.b64decode(correo['pdf_base64']), b'%PDF-1.4 fake')

        # NO se envio nada y la solicitud sigue pendiente de marcar
        enviar.assert_not_called()
        asignacion.refresh_from_db()
        self.assertFalse(asignacion.lliquidacionnotificada)

    def test_compone_no_requiere_configuracion_smtp(self):
        """Para que n8n envie no hace falta que la empresa tenga SMTP."""
        from operaciones.servicios import construir_correo_liquidacion

        asignacion = self.crear_asignacion()
        self.assertEqual(0, self.empresa.configuracioncorreos_empresa.count()
                         if hasattr(self.empresa, 'configuracioncorreos_empresa')
                         else 0)

        p1, p2 = self.parchear_envio()
        with p1, p2:
            correo = construir_correo_liquidacion(asignacion.id, self.empresa)

        self.assertTrue(correo['ok'], correo['error'])
        self.assertTrue(correo['asunto'])

    def test_marcar_tras_envio_externo(self):
        from operaciones.servicios import (construir_correo_liquidacion,
                                           marcar_liquidacion_notificada)

        asignacion = self.crear_asignacion()
        p1, p2 = self.parchear_envio()
        with p1, p2:
            construir_correo_liquidacion(asignacion.id, self.empresa)

        marca = marcar_liquidacion_notificada(asignacion.id, self.empresa)
        self.assertTrue(marca['ok'], marca['error'])
        self.assertFalse(marca['ya_estaba'])

        asignacion.refresh_from_db()
        self.assertTrue(asignacion.lliquidacionnotificada)
        self.assertIsNotNone(asignacion.dliquidacionnotificada)

    def test_marcar_no_ve_solicitudes_de_otra_empresa(self):
        from operaciones.servicios import marcar_liquidacion_notificada

        asignacion = self.crear_asignacion(empresa=self.otra_empresa)
        marca = marcar_liquidacion_notificada(asignacion.id, self.empresa)
        self.assertFalse(marca['ok'])
        self.assertIn('No existe la solicitud', marca['error'])

        asignacion.refresh_from_db()
        self.assertFalse(asignacion.lliquidacionnotificada)

    def test_compuesta_dos_veces_no_cambia_nada_hasta_marcar(self):
        from operaciones.servicios import construir_correo_liquidacion

        asignacion = self.crear_asignacion()
        p1, p2 = self.parchear_envio()
        with p1, p2:
            primera = construir_correo_liquidacion(asignacion.id, self.empresa)
            segunda = construir_correo_liquidacion(asignacion.id, self.empresa)

        self.assertTrue(primera['ok'])
        self.assertTrue(segunda['ok'])
        self.assertFalse(segunda['ya_enviada'])


class WebhookDatosTests(BaseLiquidacionTests):
    """Endpoints para el flujo que envia desde n8n."""

    def test_sin_clave_se_rechaza(self):
        from operaciones.webhooks import webhook_datos_correo_liquidacion

        respuesta = webhook_datos_correo_liquidacion(
            self.peticion_datos({'asignacion_id': 1}))
        self.assertEqual(respuesta.status_code, 403)

    def test_devuelve_un_correo_con_pdf(self):
        from operaciones.webhooks import webhook_datos_correo_liquidacion

        asignacion = self.crear_asignacion()
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_datos_correo_liquidacion(
                self.peticion_datos({'asignacion_id': asignacion.id}, plana))

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['listos'], 1)
        correo = cuerpo['correos'][0]
        self.assertEqual(correo['destinatario'], 'cliente@example.com')
        self.assertTrue(correo['pdf_base64'])
        self.assertTrue(correo['asunto'])

    def test_con_pdf_false_omite_el_adjunto(self):
        from operaciones.webhooks import webhook_datos_correo_liquidacion

        asignacion = self.crear_asignacion()
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_datos_correo_liquidacion(
                self.peticion_datos({'asignacion_id': asignacion.id,
                                     'con_pdf': 'false'}, plana))

        correo = json.loads(respuesta.content)['correos'][0]
        self.assertNotIn('pdf_base64', correo)
        self.assertTrue(correo['ok'])

    def test_lote_devuelve_las_pendientes(self):
        from operaciones.webhooks import webhook_datos_correo_liquidacion

        self.crear_asignacion(codigo='sol00001')
        self.crear_asignacion(codigo='sol00002')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_datos_correo_liquidacion(
                self.peticion_datos({'lote': 'true'}, plana))

        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['modo'], 'lote')
        self.assertEqual(cuerpo['solicitados'], 2)
        self.assertEqual(cuerpo['listos'], 2)

    def test_lote_sin_pdf_lista_los_ids(self):
        """Con con_pdf=false el flujo puede pedir solo la lista de trabajo."""
        from operaciones.webhooks import webhook_datos_correo_liquidacion

        self.crear_asignacion(codigo='sol00001')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_datos_correo_liquidacion(
                self.peticion_datos({'lote': 'true', 'con_pdf': 'false'}, plana))

        correo = json.loads(respuesta.content)['correos'][0]
        self.assertNotIn('pdf_base64', correo)
        self.assertEqual(correo['asignacion_id'], 1)

    def test_no_ve_solicitudes_de_otra_empresa(self):
        from operaciones.webhooks import webhook_datos_correo_liquidacion

        self.crear_asignacion(empresa=self.otra_empresa, codigo='sol00099')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_datos_correo_liquidacion(
                self.peticion_datos({'lote': 'true'}, plana))

        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 0)


class WebhookConfirmarTests(BaseLiquidacionTests):
    def test_confirma_y_marca(self):
        from operaciones.webhooks import webhook_confirmar_correo_liquidacion

        asignacion = self.crear_asignacion()
        _c, plana = self.crear_clave()

        respuesta = webhook_confirmar_correo_liquidacion(
            self.peticion({'asignacion_ids': [asignacion.id]}, clave=plana))

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['confirmadas'], 1)

        asignacion.refresh_from_db()
        self.assertTrue(asignacion.lliquidacionnotificada)

    def test_confirma_varias(self):
        from operaciones.webhooks import webhook_confirmar_correo_liquidacion

        a1 = self.crear_asignacion(codigo='sol00001')
        a2 = self.crear_asignacion(codigo='sol00002')
        _c, plana = self.crear_clave()

        respuesta = webhook_confirmar_correo_liquidacion(
            self.peticion({'asignacion_ids': [a1.id, a2.id]}, clave=plana))
        self.assertEqual(json.loads(respuesta.content)['confirmadas'], 2)

    def test_sin_ids_devuelve_400(self):
        from operaciones.webhooks import webhook_confirmar_correo_liquidacion

        _c, plana = self.crear_clave()
        respuesta = webhook_confirmar_correo_liquidacion(
            self.peticion({}, clave=plana))
        self.assertEqual(respuesta.status_code, 400)

    def test_no_confirma_de_otra_empresa(self):
        from operaciones.webhooks import webhook_confirmar_correo_liquidacion

        asignacion = self.crear_asignacion(empresa=self.otra_empresa)
        _c, plana = self.crear_clave(empresa=self.empresa)

        respuesta = webhook_confirmar_correo_liquidacion(
            self.peticion({'asignacion_ids': [asignacion.id]}, clave=plana))
        self.assertEqual(respuesta.status_code, 207)

        asignacion.refresh_from_db()
        self.assertFalse(asignacion.lliquidacionnotificada)

    def test_ciclo_completo_compone_envia_y_confirma(self):
        """Ciclo como lo hace n8n: componer, enviar (simulado), confirmar."""
        from operaciones.servicios import marcar_liquidacion_notificada
        from operaciones.webhooks import (webhook_confirmar_correo_liquidacion,
                                          webhook_datos_correo_liquidacion)

        asignacion = self.crear_asignacion()
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            datos = json.loads(webhook_datos_correo_liquidacion(
                self.peticion_datos({'asignacion_id': asignacion.id},
                                    plana)).content)
        self.assertEqual(datos['listos'], 1)

        # n8n enviaria aqui con el nodo de Gmail; se simula la confirmacion
        confirmacion = webhook_confirmar_correo_liquidacion(
            self.peticion({'asignacion_ids': [asignacion.id]}, clave=plana))
        self.assertEqual(confirmacion.status_code, 200)

        # la segunda corrida no vuelve a ofrecerla
        with p1, p2:
            segunda = json.loads(webhook_datos_correo_liquidacion(
                self.peticion_datos({'lote': 'true'}, plana)).content)
        self.assertEqual(segunda['solicitados'], 0)


class ModoLoteTests(BaseLiquidacionTests):
    """Modo lote: la empresa decide que notificar, sin que n8n pase ids."""

    def test_lote_vacio_responde_ok_sin_enviar(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        _c, plana = self.crear_clave()
        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = json.loads(respuesta.content)
        self.assertTrue(cuerpo['ok'])
        self.assertEqual(cuerpo['solicitados'], 0)
        self.assertEqual(cuerpo['modo'], 'lote')
        enviar.assert_not_called()

    def test_lote_envia_las_pendientes(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        self.crear_asignacion(codigo='sol00001')
        self.crear_asignacion(codigo='sol00002')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))

        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['modo'], 'lote')
        self.assertEqual(cuerpo['solicitados'], 2)
        self.assertEqual(cuerpo['enviados'], 2)

    def test_lote_ignora_las_ya_notificadas(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        a1 = self.crear_asignacion(codigo='sol00001')
        a2 = self.crear_asignacion(codigo='sol00002')
        a2.lliquidacionnotificada = True
        a2.save()
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))

        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 1)
        self.assertEqual(cuerpo['resultados'][0]['asignacion_id'], a1.id)

    def test_lote_ignora_las_no_liquidadas(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        self.crear_asignacion(estado='P', codigo='sol00009')
        _c, plana = self.crear_clave()
        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 0)

    def test_lote_no_ve_solicitudes_de_otra_empresa(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        self.crear_asignacion(empresa=self.otra_empresa, codigo='sol00099')
        self.crear_asignacion(codigo='sol00001')
        _c, plana = self.crear_clave(empresa=self.empresa)

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 1)
        self.assertEqual(cuerpo['resultados'][0]['cxasignacion'], 'sol00001')

    def test_lote_respeta_el_limite(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        for n in range(1, 4):
            self.crear_asignacion(codigo='sol0000%d' % n)
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1, p2:
            respuesta = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True, 'limite': 2}, clave=plana))
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(cuerpo['solicitados'], 2)

    def test_lote_segunda_corrida_no_reenvia(self):
        from operaciones.webhooks import webhook_enviar_correo_liquidacion

        self.crear_asignacion(codigo='sol00001')
        self.crear_asignacion(codigo='sol00002')
        _c, plana = self.crear_clave()

        p1, p2 = self.parchear_envio()
        with p1 as enviar, p2:
            primera = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))
            segunda = webhook_enviar_correo_liquidacion(
                self.peticion({'lote': True}, clave=plana))

        self.assertEqual(enviar.call_count, 2)
        c1 = json.loads(primera.content)
        c2 = json.loads(segunda.content)
        self.assertEqual(c1['enviados'], 2)
        self.assertEqual(c2['solicitados'], 0)
